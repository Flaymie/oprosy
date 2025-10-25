"""
Endpoints для загрузки и получения файлов
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid

from api.database import get_db
from api.dependencies import get_current_user
from api.config import settings
from database.models import User, File

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    quiz_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузить файл
    
    Сохраняет файл в локальное хранилище и возвращает путь
    """
    # Проверяем размер файла
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Проверяем тип файла
    allowed_types = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {file.content_type}"
        )
    
    # Генерируем уникальное имя файла
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Определяем путь для сохранения
    if quiz_id:
        upload_dir = Path(settings.UPLOAD_DIR) / f"quiz_{quiz_id}"
    else:
        upload_dir = Path(settings.UPLOAD_DIR) / "general"
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / unique_filename
    
    # Сохраняем файл
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Сохраняем метаданные в БД
    relative_path = str(file_path.relative_to(settings.UPLOAD_DIR))
    
    file_record = File(
        quiz_id=quiz_id,
        user_id=current_user.id,
        file_path=relative_path,
        file_type=file.content_type,
        file_size=file_size
    )
    
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    
    return {
        "file_id": file_record.id,
        "file_path": relative_path,
        "file_url": f"/api/files/{file_record.id}",
        "file_size": file_size,
        "file_type": file.content_type
    }


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить файл по ID
    
    Возвращает файл для скачивания
    """
    # Находим файл в БД
    file_record = db.query(File).filter(File.id == file_id).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Формируем полный путь к файлу
    file_path = Path(settings.UPLOAD_DIR) / file_record.file_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Возвращаем файл
    return FileResponse(
        path=str(file_path),
        media_type=file_record.file_type,
        filename=file_path.name
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить файл
    
    Только владелец файла или администратор может удалить
    """
    # Находим файл в БД
    file_record = db.query(File).filter(File.id == file_id).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Проверяем права доступа
    if file_record.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Удаляем файл с диска
    file_path = Path(settings.UPLOAD_DIR) / file_record.file_path
    
    if file_path.exists():
        os.remove(file_path)
    
    # Удаляем запись из БД
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully"}
