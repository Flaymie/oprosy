"""
Endpoints для аналитики и экспорта данных
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from collections import Counter
import io
import csv
import json

from api.database import get_db
from api.dependencies import get_current_admin
from database.models import User, Quiz, Response

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{quiz_id}")
async def get_quiz_analytics(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Получить аналитику по опросу
    
    Возвращает агрегированные данные для построения графиков
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Проверяем права доступа
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем все ответы
    responses = db.query(Response).filter(Response.quiz_id == quiz_id).all()
    
    if not responses:
        return {
            "quiz_id": quiz_id,
            "title": quiz.title,
            "total_responses": 0,
            "questions_analytics": {}
        }
    
    # Анализируем ответы по вопросам
    questions_analytics = {}
    
    # Получаем структуру опроса
    structure = quiz.structure
    questions = structure.get("questions", [])
    
    for question in questions:
        question_id = question.get("id")
        question_type = question.get("type")
        question_text = question.get("text")
        
        # Собираем все ответы на этот вопрос
        answers_for_question = []
        for response in responses:
            answer = response.answers.get(question_id)
            if answer is not None:
                answers_for_question.append(answer)
        
        # Анализируем в зависимости от типа вопроса
        if question_type in ["radio", "checkbox"]:
            # Подсчитываем частоту выбора каждого варианта
            answer_counts = Counter(
                ans if isinstance(ans, str) else json.dumps(ans)
                for ans in answers_for_question
            )
            
            questions_analytics[question_id] = {
                "question": question_text,
                "type": question_type,
                "total_answers": len(answers_for_question),
                "distribution": dict(answer_counts)
            }
        
        elif question_type == "scale":
            # Для шкалы считаем среднее и распределение
            numeric_answers = [int(ans) for ans in answers_for_question if isinstance(ans, (int, str)) and str(ans).isdigit()]
            
            if numeric_answers:
                avg_score = sum(numeric_answers) / len(numeric_answers)
                answer_counts = Counter(numeric_answers)
                
                questions_analytics[question_id] = {
                    "question": question_text,
                    "type": question_type,
                    "total_answers": len(numeric_answers),
                    "average": round(avg_score, 2),
                    "distribution": dict(answer_counts)
                }
        
        elif question_type == "text":
            # Для текстовых ответов просто считаем количество
            questions_analytics[question_id] = {
                "question": question_text,
                "type": question_type,
                "total_answers": len(answers_for_question),
                "sample_answers": answers_for_question[:5]  # Первые 5 ответов для примера
            }
    
    return {
        "quiz_id": quiz_id,
        "title": quiz.title,
        "total_responses": len(responses),
        "questions_analytics": questions_analytics
    }


@router.get("/{quiz_id}/export")
async def export_quiz_responses(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Экспортировать ответы в CSV
    
    Только для создателя опроса
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Проверяем права доступа
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем все ответы с данными пользователей
    responses = db.query(
        Response,
        User.telegram_id,
        User.username,
        User.first_name,
        User.email
    ).join(
        User, Response.user_id == User.id
    ).filter(
        Response.quiz_id == quiz_id
    ).order_by(
        Response.completed_at
    ).all()
    
    if not responses:
        raise HTTPException(status_code=404, detail="No responses found")
    
    # Получаем структуру опроса для заголовков
    structure = quiz.structure
    questions = structure.get("questions", [])
    
    # Создаем CSV в памяти
    output = io.StringIO()
    
    # Формируем заголовки
    headers = ["user_id", "telegram_id", "username", "first_name", "email", "completed_at"]
    for question in questions:
        headers.append(f"q_{question.get('id')}")
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    # Записываем данные
    for resp, telegram_id, username, first_name, email in responses:
        row = {
            "user_id": resp.user_id,
            "telegram_id": telegram_id,
            "username": username or "",
            "first_name": first_name or "",
            "email": email or "",
            "completed_at": resp.completed_at.isoformat()
        }
        
        # Добавляем ответы на вопросы
        for question in questions:
            question_id = question.get("id")
            answer = resp.answers.get(question_id, "")
            
            # Преобразуем сложные ответы в строку
            if isinstance(answer, (dict, list)):
                answer = json.dumps(answer, ensure_ascii=False)
            
            row[f"q_{question_id}"] = answer
        
        writer.writerow(row)
    
    # Возвращаем CSV файл
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=quiz_{quiz_id}_responses.csv"
        }
    )
