from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from minio import Minio
from minio.error import S3Error
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# MinIO配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "standards")

# 初始化MinIO客户端
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """上传文件"""
    try:
        # 检查存储桶是否存在
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        object_name = f"files/{uuid.uuid4()}{file_extension}"
        
        # 上传文件
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            file.file,
            length=-1,
            part_size=10*1024*1024,
            content_type=file.content_type
        )
        
        # 返回文件路径
        file_path = f"/{MINIO_BUCKET}/{object_name}"
        return {"file_path": file_path}
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {e}"
        )

@router.get("/download/{object_name}")
async def download_file(
    object_name: str,
    current_user = Depends(get_current_user)
):
    """下载文件"""
    try:
        # 获取对象
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        
        # 生成文件名
        filename = os.path.basename(object_name)
        
        # 返回流式响应
        return StreamingResponse(
            response,
            media_type=response.headers.get("Content-Type", "application/octet-stream"),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {e}"
        )

@router.get("/preview/{object_name}")
async def preview_file(
    object_name: str,
    current_user = Depends(get_current_user)
):
    """预览文件"""
    try:
        # 获取对象
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        
        # 生成文件名
        filename = os.path.basename(object_name)
        
        # 返回流式响应
        return StreamingResponse(
            response,
            media_type=response.headers.get("Content-Type", "application/octet-stream"),
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview file: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview file: {e}"
        )
