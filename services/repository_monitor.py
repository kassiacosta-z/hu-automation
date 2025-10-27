"""
[OBSOLETO] Substituído por coleta via Gmail/Drive.
Mantido temporariamente para compatibilidade até migração completa.
"""

import os
import hashlib
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from database import SessionLocal
from models import TranscriptionJob, JobStatus
from config import config


class RepositoryMonitor:
    """Monitor de repositório para detectar arquivos de transcrição."""
    
    def __init__(self, repo_path: str = None):
        """
        Inicializa o monitor de repositório.
        
        Args:
            repo_path: Caminho do repositório (opcional, usa config se não fornecido)
        """
        self.repo_path = repo_path or getattr(config, 'TRANSCRIPTION_REPO_PATH', None)
        if not self.repo_path:
            raise ValueError("Caminho do repositório não configurado")
        
        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repositório não encontrado: {self.repo_path}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calcula hash SHA-256 de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Hash SHA-256 do arquivo
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            raise Exception(f"Erro ao calcular hash do arquivo {file_path}: {str(e)}")
    
    def _get_file_patterns(self) -> List[str]:
        """
        Retorna padrões de arquivos para buscar.
        
        Returns:
            Lista de padrões glob para arquivos de transcrição
        """
        return [
            "*AnotaçõesdoGemini*",
            "*.docx",
            "*.txt", 
            "*.pdf",
            "*.doc"
        ]
    
    def _find_transcription_files(self) -> List[Dict[str, Any]]:
        """
        Encontra todos os arquivos de transcrição no repositório.
        
        Returns:
            Lista de dicionários com informações dos arquivos encontrados
        """
        files_found = []
        patterns = self._get_file_patterns()
        
        for pattern in patterns:
            search_path = os.path.join(self.repo_path, "**", pattern)
            for file_path in glob.glob(search_path, recursive=True):
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        file_info = {
                            'path': file_path,
                            'name': os.path.basename(file_path),
                            'size': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_ctime),
                            'modified_at': datetime.fromtimestamp(stat.st_mtime),
                            'relative_path': os.path.relpath(file_path, self.repo_path)
                        }
                        files_found.append(file_info)
                    except Exception as e:
                        print(f"Erro ao processar arquivo {file_path}: {str(e)}")
                        continue
        
        return files_found
    
    def _get_existing_jobs(self) -> Dict[str, TranscriptionJob]:
        """
        Obtém jobs existentes do banco de dados.
        
        Returns:
            Dicionário com hash como chave e TranscriptionJob como valor
        """
        session = SessionLocal()
        try:
            jobs = session.query(TranscriptionJob).all()
            return {job.source_hash: job for job in jobs}
        finally:
            session.close()
    
    def _create_job_record(self, file_info: Dict[str, Any], file_hash: str) -> TranscriptionJob:
        """
        Cria um novo registro de job no banco de dados.
        
        Args:
            file_info: Informações do arquivo
            file_hash: Hash do arquivo
            
        Returns:
            TranscriptionJob criado
        """
        session = SessionLocal()
        try:
            job = TranscriptionJob(
                source_uri=file_info['path'],
                source_hash=file_hash,
                status=JobStatus.DISCOVERED,
                attempts=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao criar job no banco: {str(e)}")
        finally:
            session.close()
    
    def scan_repository(self) -> Dict[str, Any]:
        """
        Escaneia o repositório e registra arquivos novos.
        
        Returns:
            Dicionário com estatísticas do scan
        """
        try:
            # Encontrar arquivos no repositório
            files_found = self._find_transcription_files()
            
            # Obter jobs existentes
            existing_jobs = self._get_existing_jobs()
            
            # Processar arquivos encontrados
            new_files = []
            existing_files = []
            errors = []
            
            for file_info in files_found:
                try:
                    # Calcular hash do arquivo
                    file_hash = self._calculate_file_hash(file_info['path'])
                    
                    # Verificar se já existe
                    if file_hash in existing_jobs:
                        existing_files.append({
                            'file_info': file_info,
                            'job': existing_jobs[file_hash],
                            'hash': file_hash
                        })
                    else:
                        # Criar novo job
                        job = self._create_job_record(file_info, file_hash)
                        new_files.append({
                            'file_info': file_info,
                            'job': job,
                            'hash': file_hash
                        })
                        
                except Exception as e:
                    errors.append({
                        'file_path': file_info['path'],
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'stats': {
                    'total_found': len(files_found),
                    'new_files': len(new_files),
                    'existing_files': len(existing_files),
                    'errors': len(errors)
                },
                'new_files': new_files,
                'existing_files': existing_files,
                'errors': errors,
                'scan_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stats': {
                    'total_found': 0,
                    'new_files': 0,
                    'existing_files': 0,
                    'errors': 1
                }
            }
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do repositório e banco de dados.
        
        Returns:
            Dicionário com estatísticas
        """
        session = SessionLocal()
        try:
            # Estatísticas do banco
            total_jobs = session.query(TranscriptionJob).count()
            discovered_jobs = session.query(TranscriptionJob).filter(
                TranscriptionJob.status == JobStatus.DISCOVERED
            ).count()
            processed_jobs = session.query(TranscriptionJob).filter(
                TranscriptionJob.status == JobStatus.PROCESSED
            ).count()
            failed_jobs = session.query(TranscriptionJob).filter(
                TranscriptionJob.status == JobStatus.FAILED
            ).count()
            
            # Estatísticas do repositório
            files_found = self._find_transcription_files()
            
            return {
                'success': True,
                'repository': {
                    'path': self.repo_path,
                    'files_found': len(files_found)
                },
                'database': {
                    'total_jobs': total_jobs,
                    'discovered': discovered_jobs,
                    'processed': processed_jobs,
                    'failed': failed_jobs
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            session.close()
    
    def get_recent_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtém jobs recentes do banco de dados.
        
        Args:
            limit: Número máximo de jobs a retornar
            
        Returns:
            Lista de jobs recentes
        """
        session = SessionLocal()
        try:
            jobs = session.query(TranscriptionJob).order_by(
                TranscriptionJob.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': job.id,
                    'source_uri': job.source_uri,
                    'source_hash': job.source_hash,
                    'status': job.status,
                    'attempts': job.attempts,
                    'created_at': job.created_at.isoformat(),
                    'updated_at': job.updated_at.isoformat(),
                    'filename': os.path.basename(job.source_uri)
                }
                for job in jobs
            ]
        except Exception as e:
            return []
        finally:
            session.close()