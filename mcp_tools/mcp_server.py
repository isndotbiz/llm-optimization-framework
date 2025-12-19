#!/usr/bin/env python3
"""
MCP Server for AI Router
Provides PDF reading, web data storage, and data retrieval tools
Following the Model Context Protocol specification
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger('mcp_server')

# Try to import PDF libraries
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        PDF_LIBRARY = None
        logger.warning("No PDF library available. Install pdfplumber or PyPDF2")


class MCPServer:
    """MCP Server implementing JSON-RPC over stdio"""

    def __init__(self):
        self.tools = {
            'read_pdf': self.read_pdf,
            'store_web_data': self.store_web_data,
            'retrieve_stored_data': self.retrieve_stored_data,
            'store_pdf': self.store_pdf
        }
        self.base_projects_dir = Path(r'D:\models\projects')
        logger.info("MCP Server initialized")

    def read_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF files

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing:
            - text: Extracted text content
            - page_count: Number of pages
            - metadata: PDF metadata (title, author, etc.)
            - success: Boolean indicating success
            - error: Error message if failed
        """
        try:
            pdf_path = Path(file_path)

            if not pdf_path.exists():
                return {
                    'success': False,
                    'error': f'PDF file not found: {file_path}',
                    'text': '',
                    'page_count': 0,
                    'metadata': {}
                }

            if PDF_LIBRARY == 'pdfplumber':
                return self._read_pdf_pdfplumber(pdf_path)
            elif PDF_LIBRARY == 'PyPDF2':
                return self._read_pdf_pypdf2(pdf_path)
            else:
                return {
                    'success': False,
                    'error': 'No PDF library installed. Install pdfplumber or PyPDF2',
                    'text': '',
                    'page_count': 0,
                    'metadata': {}
                }

        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'page_count': 0,
                'metadata': {}
            }

    def _read_pdf_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """Read PDF using pdfplumber library"""
        text_content = []
        metadata = {}

        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata
            if pdf.metadata:
                metadata = {k: str(v) for k, v in pdf.metadata.items() if v is not None}

            # Extract text from all pages
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)

        return {
            'success': True,
            'text': '\n\n'.join(text_content),
            'page_count': page_count,
            'metadata': metadata,
            'file_path': str(pdf_path),
            'file_size': pdf_path.stat().st_size
        }

    def _read_pdf_pypdf2(self, pdf_path: Path) -> Dict[str, Any]:
        """Read PDF using PyPDF2 library"""
        text_content = []
        metadata = {}

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract metadata
            if pdf_reader.metadata:
                metadata = {k: str(v) for k, v in pdf_reader.metadata.items() if v is not None}

            # Extract text from all pages
            page_count = len(pdf_reader.pages)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)

        return {
            'success': True,
            'text': '\n\n'.join(text_content),
            'page_count': page_count,
            'metadata': metadata,
            'file_path': str(pdf_path),
            'file_size': pdf_path.stat().st_size
        }

    def store_web_data(self, query: str, results: Union[Dict, List, str],
                       project_name: str) -> Dict[str, Any]:
        """
        Store web search results or fetched web data

        Args:
            query: Search query or data identifier
            results: Web search results (JSON serializable)
            project_name: Name of the project

        Returns:
            Dictionary with:
            - success: Boolean
            - storage_path: Path where data was stored
            - timestamp: When data was stored
            - error: Error message if failed
        """
        try:
            # Create project directory structure
            project_dir = self.base_projects_dir / project_name
            data_dir = project_dir / 'data' / 'web_search'

            # Organize by date
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_dir = data_dir / date_str
            date_dir.mkdir(parents=True, exist_ok=True)

            # Create safe filename from query
            safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_'
                                for c in query)
            safe_query = safe_query.strip().replace(' ', '_')[:100]

            # Add timestamp to ensure uniqueness
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_query}_{timestamp}.json"
            file_path = date_dir / filename

            # Prepare data structure
            data_to_store = {
                'query': query,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'project_name': project_name
            }

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_store, f, indent=2, ensure_ascii=False)

            logger.info(f"Stored web data for query '{query}' in project '{project_name}'")

            return {
                'success': True,
                'storage_path': str(file_path),
                'timestamp': data_to_store['timestamp'],
                'query': query,
                'project_name': project_name
            }

        except Exception as e:
            logger.error(f"Error storing web data: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'storage_path': '',
                'timestamp': ''
            }

    def retrieve_stored_data(self, project_name: str,
                            query: Optional[str] = None,
                            date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retrieve previously stored web data

        Args:
            project_name: Name of the project
            query: Optional query filter (substring match)
            date_range: Optional date range with 'start' and 'end' keys (YYYY-MM-DD)

        Returns:
            Dictionary with:
            - success: Boolean
            - data: List of matching stored data entries
            - count: Number of entries found
            - error: Error message if failed
        """
        try:
            project_dir = self.base_projects_dir / project_name
            data_dir = project_dir / 'data' / 'web_search'

            if not data_dir.exists():
                return {
                    'success': True,
                    'data': [],
                    'count': 0,
                    'message': f'No web search data found for project {project_name}'
                }

            # Collect all JSON files
            matching_data = []

            for json_file in data_dir.rglob('*.json'):
                # Check date range if specified
                if date_range:
                    date_str = json_file.parent.name
                    try:
                        file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        start_date = datetime.strptime(date_range.get('start', '1900-01-01'),
                                                      '%Y-%m-%d').date()
                        end_date = datetime.strptime(date_range.get('end', '2100-12-31'),
                                                    '%Y-%m-%d').date()

                        if not (start_date <= file_date <= end_date):
                            continue
                    except ValueError:
                        pass  # Skip date filtering if parsing fails

                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Filter by query if specified
                    if query and query.lower() not in data.get('query', '').lower():
                        continue

                    # Add file metadata
                    data['_file_path'] = str(json_file)
                    data['_file_date'] = json_file.parent.name

                    matching_data.append(data)

                except Exception as e:
                    logger.warning(f"Error reading file {json_file}: {str(e)}")
                    continue

            # Sort by timestamp (newest first)
            matching_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            logger.info(f"Retrieved {len(matching_data)} data entries for project '{project_name}'")

            return {
                'success': True,
                'data': matching_data,
                'count': len(matching_data),
                'project_name': project_name
            }

        except Exception as e:
            logger.error(f"Error retrieving stored data: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'count': 0
            }

    def store_pdf(self, pdf_path: str, project_name: str,
                  tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Copy PDF to project data folder and index it

        Args:
            pdf_path: Path to the PDF file
            project_name: Name of the project
            tags: Optional list of tags for categorization

        Returns:
            Dictionary with:
            - success: Boolean
            - storage_path: Where PDF was stored
            - index_path: Path to metadata index
            - error: Error message if failed
        """
        try:
            source_path = Path(pdf_path)

            if not source_path.exists():
                return {
                    'success': False,
                    'error': f'PDF file not found: {pdf_path}',
                    'storage_path': '',
                    'index_path': ''
                }

            # Create project directory structure
            project_dir = self.base_projects_dir / project_name
            pdfs_dir = project_dir / 'data' / 'pdfs'
            pdfs_dir.mkdir(parents=True, exist_ok=True)

            # Copy PDF with timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            dest_path = pdfs_dir / pdf_filename

            shutil.copy2(source_path, dest_path)

            # Read PDF metadata
            pdf_info = self.read_pdf(str(dest_path))

            # Create metadata index entry
            index_path = pdfs_dir / 'index.json'

            # Load existing index or create new
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {'pdfs': []}

            # Create metadata entry
            metadata_entry = {
                'filename': pdf_filename,
                'original_path': str(source_path),
                'storage_path': str(dest_path),
                'timestamp': datetime.now().isoformat(),
                'tags': tags or [],
                'page_count': pdf_info.get('page_count', 0),
                'file_size': dest_path.stat().st_size,
                'pdf_metadata': pdf_info.get('metadata', {})
            }

            # Add to index
            index['pdfs'].append(metadata_entry)

            # Write updated index
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)

            logger.info(f"Stored PDF '{pdf_filename}' in project '{project_name}'")

            return {
                'success': True,
                'storage_path': str(dest_path),
                'index_path': str(index_path),
                'filename': pdf_filename,
                'page_count': pdf_info.get('page_count', 0),
                'tags': tags or []
            }

        except Exception as e:
            logger.error(f"Error storing PDF: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'storage_path': '',
                'index_path': ''
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')

            if method not in self.tools:
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32601,
                        'message': f'Method not found: {method}'
                    },
                    'id': request_id
                }

            # Call the tool
            result = self.tools[method](**params)

            return {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }

        except Exception as e:
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                },
                'id': request.get('id')
            }

    def run(self):
        """Run MCP server on stdio"""
        logger.info("MCP Server starting...")
        logger.info(f"Available tools: {list(self.tools.keys())}")

        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {str(e)}")
                    error_response = {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': -32700,
                            'message': 'Parse error'
                        },
                        'id': None
                    }
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            logger.info("MCP Server shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)


def main():
    """Main entry point"""
    server = MCPServer()
    server.run()


if __name__ == '__main__':
    main()
