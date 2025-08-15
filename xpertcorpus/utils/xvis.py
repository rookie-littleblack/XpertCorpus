"""
JSONL Visualization Tool - For viewing and browsing JSONL corpus files in the project.

@author: rookielittleblack
@date:   2025-08-15
"""
import re
import os
import sys
import json
import markdown
import pandas as pd
import streamlit as st

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from xpertcorpus.utils.xlogger import xlogger


class JSONLViewer:
    """JSONL file viewer for browsing corpus data."""
    
    def __init__(self):
        self.data: List[Dict] = []
        self.filtered_data: List[Dict] = []
        self.current_index: int = 0
        self.max_records: int = 1000
        self.total_records_in_files: int = 0  # Track total records in source files
        
    def load_files(self, file_paths: List[str], max_records: int = 1000) -> bool:
        """
        Load JSONL files into the viewer.
        
        Args:
            file_paths: List of file paths to load
            max_records: Maximum total number of records to load
            
        Returns:
            bool: Whether the files were successfully loaded
        """
        self.max_records = max_records
        self.data = []
        self.total_records_in_files = 0
        
        if not file_paths:
            return False
            
        # Calculate maximum records per file
        records_per_file = max_records // len(file_paths)
        
        for file_path in file_paths:
            file_path = file_path.strip()
            if not file_path:
                continue
                
            try:
                if not os.path.exists(file_path):
                    st.error(f"File not found: {file_path}")
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    count = 0
                    file_total_count = 0
                    for line in f:
                        file_total_count += 1  # Count total lines in file
                        if count >= records_per_file:
                            continue  # Skip loading but still count
                        try:
                            data = json.loads(line.strip())
                            data['_source_file'] = file_path  # Add source file identifier
                            self.data.append(data)
                            count += 1
                        except json.JSONDecodeError as e:
                            if count < records_per_file:
                                st.warning(f"Skipping invalid JSON line ({file_path}): {e}")
                            continue
                    
                    self.total_records_in_files += file_total_count
                    xlogger.info(f"File {file_path}: {file_total_count} total records, loaded {count}")
                            
            except Exception as e:
                st.error(f"Failed to read file {file_path}: {e}")
                
        self.filtered_data = self.data.copy()
        self.current_index = 0
        
        return len(self.data) > 0
    
    def get_available_fields(self) -> List[str]:
        """Get all available field names from loaded data."""
        if not self.data:
            return []
            
        fields = set()
        for record in self.data:
            fields.update(record.keys())
            
        # Exclude internal fields
        fields.discard('_source_file')
        return sorted(list(fields))
    
    def search(self, field: str, keyword: str) -> List[Dict]:
        """
        Search for keywords in the specified field.
        
        Args:
            field: Field name to search in
            keyword: Keyword to search for
            
        Returns:
            List[Dict]: List of matching records
        """
        if not keyword or not field:
            self.filtered_data = self.data.copy()
        else:
            self.filtered_data = []
            keyword_lower = keyword.lower()
            
            for record in self.data:
                if field in record:
                    field_value = str(record[field]).lower()
                    if keyword_lower in field_value:
                        self.filtered_data.append(record)
                        
        self.current_index = 0
        return self.filtered_data
    
    def navigate(self, direction: int) -> Optional[Dict]:
        """
        Navigate to a record in the specified direction.
        
        Args:
            direction: Direction to navigate (-1: previous, 1: next)
            
        Returns:
            Optional[Dict]: Current record after navigation
        """
        if not self.filtered_data:
            return None
            
        self.current_index += direction
        self.current_index = max(0, min(self.current_index, len(self.filtered_data) - 1))
        
        return self.filtered_data[self.current_index] if self.filtered_data else None
    
    def get_current_record(self) -> Optional[Dict]:
        """Get the current record being viewed."""
        if not self.filtered_data or self.current_index >= len(self.filtered_data):
            return None
        return self.filtered_data[self.current_index]
    
    def render_field(self, field_name: str, field_value: Any) -> str:
        """
        Render field content in Markdown format.
        
        Args:
            field_name: Name of the field
            field_value: Value of the field
            
        Returns:
            str: Rendered HTML content
        """
        if field_value is None:
            content = "N/A"
        elif isinstance(field_value, (dict, list)):
            content = f"```json\n{json.dumps(field_value, ensure_ascii=False, indent=2)}\n```"
        else:
            content = str(field_value)
            
        #markdown_content = f"### {field_name}\n\n{content}"
        markdown_content = f"{content}"
        
        # Convert to HTML
        html = markdown.markdown(markdown_content, extensions=['codehilite', 'fenced_code'])
        
        return html


def main():
    """Main function - Streamlit application entry point."""
    st.set_page_config(
        page_title="XpertCorpus-Vis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Hide Streamlit default header and reduce top padding
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize viewer
    if 'viewer' not in st.session_state:
        st.session_state.viewer = JSONLViewer()
    
    viewer = st.session_state.viewer
    
    # Create two-column layout
    col_left, col_right = st.columns([1, 3])
    
    # Left control panel
    with col_left:
        st.markdown("""
        <style>
        .left-panel {
            height: 90vh;
            overflow-y: auto;
            padding-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            # Page title
            st.markdown("# 📊 XpertCorpus-Vis")
            
            # File path input
            st.markdown("### 📁 File Paths")
            file_paths_input = st.text_area(
                "JSONL file paths (one per line)",
                height=120,
                placeholder="Example:\n/path/to/file1.jsonl\n/path/to/file2.jsonl",
                help="Enter full paths to JSONL files, one file per line",
                label_visibility="collapsed"
            )
            
            # Maximum records setting
            max_records = st.number_input(
                "Max Records",
                min_value=10,
                max_value=1000000,
                value=1000,
                step=10,
                help="Maximum total number of records to load from all files"
            )
            
            # Load files button
            if st.button("🔄 Load Files", type="primary", use_container_width=True):
                if file_paths_input.strip():
                    file_paths = [line.strip() for line in file_paths_input.strip().split('\n') if line.strip()]
                    
                    with st.spinner("Loading files..."):
                        success = viewer.load_files(file_paths, max_records)
                        
                    if success:
                        st.success(f"Successfully loaded {len(viewer.data)} records")
                        xlogger.info(f"Loaded {len(viewer.data)} records from {len(file_paths)} files")
                    else:
                        st.error("Failed to load files, please check file paths")
                        xlogger.error("Failed to load JSONL files")
                else:
                    st.error("Please enter file paths")
            
            # Data statistics
            if viewer.data:
                st.markdown("### 📊 Data Statistics")
                
                # Create info columns
                stat_col1, stat_col2 = st.columns([4, 5])
                
                with stat_col1:
                    if viewer.filtered_data and len(viewer.filtered_data) != len(viewer.data):
                        st.info(f"🔍 **Filtered**: {len(viewer.filtered_data)}")
                    else:
                        # Get unique source files for display
                        unique_files = set()
                        for record in viewer.data:
                            if '_source_file' in record:
                                unique_files.add(record['_source_file'])
                        st.info(f"📄 **Source Files**: {len(unique_files)}")

                with stat_col2:
                    st.info(f"📚 **Total in Files**: {viewer.total_records_in_files}")
                
                # Search functionality
                st.markdown("### 🔍 Search")
                
                fields = viewer.get_available_fields()
                selected_field = st.selectbox("Select Field", fields if fields else ["No available fields"])
                
                # Initialize search keyword in session state if not exists
                if 'search_keyword' not in st.session_state:
                    st.session_state.search_keyword = ""
                
                search_keyword = st.text_input(
                    "Search Keyword", 
                    value=st.session_state.search_keyword,
                    placeholder="Enter keyword...",
                    key="search_input"
                )
                
                # Search and Reset buttons in the same row
                search_col, reset_col = st.columns([5, 2])
                
                with search_col:
                    if st.button("🔍 Search", type="primary", use_container_width=True):
                        if fields and search_keyword:
                            st.session_state.search_keyword = search_keyword
                            results = viewer.search(selected_field, search_keyword)
                            st.success(f"Found {len(results)} matching records")
                            xlogger.info(f"Search completed: {len(results)} results for '{search_keyword}' in field '{selected_field}'")
                        elif not search_keyword:
                            # If search keyword is empty, reset to show all data
                            st.session_state.search_keyword = ""
                            viewer.filtered_data = viewer.data.copy()
                            viewer.current_index = 0
                            st.success(f"Showing all {len(viewer.data)} records")
                
                with reset_col:
                    if st.button("🔄 Reset", type="secondary", use_container_width=True):
                        # Clear search and reset to all data
                        st.session_state.search_keyword = ""
                        viewer.filtered_data = viewer.data.copy()
                        viewer.current_index = 0
                        st.rerun()
    
    # Right record details panel
    with col_right:
        st.markdown("""
        <style>
        .right-panel {
            height: 90vh;
            overflow-y: auto;
            padding-left: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            if not viewer.data:
                st.markdown("## 👈 Please enter file paths on the left and click 'Load Files' to start")
            else:
                current_record = viewer.get_current_record()
                if current_record:
                    st.markdown("## 📄 Record Details")
                    
                    # Enhanced Navigation controls in one row
                    if viewer.data and viewer.filtered_data:
                        st.markdown("""
                        <style>
                        .nav-container {
                            background: linear-gradient(90deg, #f0f2f6, #ffffff);
                            padding: 8px 12px;
                            border-radius: 8px;
                            border: 1px solid #e1e5e9;
                            margin: 8px 0;
                        }
                        .stButton > button {
                            height: 2.5rem;
                            border-radius: 6px;
                            font-weight: 500;
                        }
                        .nav-info {
                            color: #555;
                            font-weight: 500;
                            line-height: 2.5rem;
                            text-align: center;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        with st.container():
                            nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 2, 1.5, 1])
                            
                            with nav_col1:
                                if st.button("⬅️ Prev", use_container_width=True, disabled=(viewer.current_index <= 0)):
                                    viewer.navigate(-1)
                                    st.rerun()
                            
                            with nav_col2:
                                if st.button("➡️ Next", use_container_width=True, disabled=(viewer.current_index >= len(viewer.filtered_data) - 1)):
                                    viewer.navigate(1)
                                    st.rerun()
                            
                            with nav_col3:
                                st.markdown(f'<div class="nav-info">📍 {viewer.current_index + 1} / {len(viewer.filtered_data)} records</div>', unsafe_allow_html=True)
                            
                            with nav_col4:
                                # Use session state to manage the jump input value
                                if 'jump_target' not in st.session_state:
                                    st.session_state.jump_target = viewer.current_index + 1
                                
                                # Update jump target when navigation happens
                                if st.session_state.jump_target != viewer.current_index + 1:
                                    st.session_state.jump_target = viewer.current_index + 1
                                
                                target_index = st.number_input(
                                    "Jump to", 
                                    min_value=1, 
                                    max_value=len(viewer.filtered_data),
                                    value=st.session_state.jump_target,
                                    key="nav_input",
                                    label_visibility="collapsed"
                                )
                            
                            with nav_col5:
                                if st.button("🎯 Go", use_container_width=True):
                                    new_index = target_index - 1
                                    if 0 <= new_index < len(viewer.filtered_data):
                                        viewer.current_index = new_index
                                        st.session_state.jump_target = target_index
                                        st.rerun()
                    
                    # Display source file information (only if there are multiple unique source files)
                    if '_source_file' in current_record:
                        # Get all unique source files from all data
                        unique_source_files = set()
                        for record in viewer.data:
                            if '_source_file' in record:
                                unique_source_files.add(record['_source_file'])
                        
                        # Only show source file info if there are multiple files
                        if len(unique_source_files) > 1:
                            st.info(f"📁 Source File: {current_record['_source_file']}")
                    
                    # Get all fields, exclude internal fields
                    all_field_names = [name for name in sorted(current_record.keys()) if not name.startswith('_')]
                    
                    # Process fields to merge tokens fields with their base fields
                    display_fields = {}
                    tokens_fields = {}
                    
                    # First, identify tokens fields and their base fields
                    for field_name in all_field_names:
                        if field_name.endswith('_tokens'):
                            base_name = field_name[:-7]  # Remove '_tokens' suffix
                            if base_name in all_field_names:
                                tokens_fields[base_name] = field_name
                            else:
                                # If no base field exists, treat as regular field
                                display_fields[field_name] = current_record[field_name]
                        else:
                            display_fields[field_name] = current_record[field_name]
                    
                    # Merge tokens fields with their base fields
                    for base_name, tokens_field in tokens_fields.items():
                        if base_name in display_fields:
                            tokens_value = current_record[tokens_field]
                            base_value = current_record[base_name]
                            
                            # Create merged content
                            merged_content = f"[Tokens count] {tokens_value}\n\n---\n\n{base_value}"
                            display_fields[base_name] = merged_content
                    
                    if display_fields:
                        # Get display field names and reverse order
                        field_names = list(display_fields.keys())
                        reversed_field_names = list(reversed(field_names))
                        
                        # Create tabs with reversed field order
                        tabs = st.tabs([f"{field_name}" for field_name in reversed_field_names])
                        
                        # Render content for each tab
                        for i, field_name in enumerate(reversed_field_names):
                            with tabs[i]:
                                # Add copy button for content fields
                                if 'content' in field_name.lower():
                                    # Get the original field value (not merged)
                                    original_value = current_record[field_name]
                                    if isinstance(original_value, str):
                                        # Create copy button with original text
                                        copy_col1, copy_col2 = st.columns([8, 1])
                                        with copy_col1:
                                            field_value = display_fields[field_name]
                                            rendered_html = viewer.render_field(field_name, field_value)
                                            st.markdown(rendered_html, unsafe_allow_html=True)
                                        with copy_col2:
                                            if st.button("📋", key=f"copy_{field_name}_{i}", help="Copy original content"):
                                                # Note: Streamlit doesn't have built-in clipboard API
                                                # We'll show the content in a text area for manual copy
                                                st.text_area(
                                                    "Copy this content:",
                                                    value=original_value,
                                                    height=200,
                                                    key=f"copy_area_{field_name}_{i}"
                                                )
                                    else:
                                        # Non-string content, just display
                                        field_value = display_fields[field_name]
                                        rendered_html = viewer.render_field(field_name, field_value)
                                        st.markdown(rendered_html, unsafe_allow_html=True)
                                else:
                                    # Regular field display
                                    field_value = display_fields[field_name]
                                    rendered_html = viewer.render_field(field_name, field_value)
                                    st.markdown(rendered_html, unsafe_allow_html=True)
                        
                    else:
                        st.warning("No displayable fields in current record")
                else:
                    st.warning("No records to display")
    
    # Footer information
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        🛠️ XpertCorpus-Vis | Support for multi-file loading, field search, navigation browsing
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()