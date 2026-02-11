"""
Excel exporter for food diary
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional
from database import DatabaseManager


class ExcelExporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        Path("exports").mkdir(exist_ok=True)
    
    def export_to_excel(
        self, 
        user_id: int, 
        filename: Optional[str] = None
    ) -> str:
        """Export all meals to Excel file"""
        meals = self.db.get_all_meals(user_id)
        
        if not meals:
            raise ValueError("Nessun pasto da esportare")
        
        # Convert to DataFrame
        df = pd.DataFrame(meals, columns=[
            'ID', 'User ID', 'Username', 'Descrizione', 'Foto', 'Data e Ora'
        ])
        
        # Format timestamp
        df['Data e Ora'] = pd.to_datetime(df['Data e Ora'])
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/diario_alimentare_{timestamp}.xlsx"
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Diario Alimentare', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Diario Alimentare']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4CAF50',
                'font_color': 'white',
                'border': 1
            })
            
            # Write headers with format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            worksheet.set_column('A:A', 8)   # ID
            worksheet.set_column('B:B', 10)  # User ID
            worksheet.set_column('C:C', 15)  # Username
            worksheet.set_column('D:D', 50)  # Descrizione
            worksheet.set_column('E:E', 30)  # Foto
            worksheet.set_column('F:F', 20)  # Data e Ora
        
        return filename
    
    def export_date_range_to_excel(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        filename: Optional[str] = None
    ) -> str:
        """Export meals within a date range to Excel"""
        meals = self.db.get_meals_by_date_range(user_id, start_date, end_date)
        
        if not meals:
            raise ValueError(f"Nessun pasto nel periodo {start_date} - {end_date}")
        
        df = pd.DataFrame(meals, columns=[
            'ID', 'User ID', 'Username', 'Descrizione', 'Foto', 'Data e Ora'
        ])
        
        df['Data e Ora'] = pd.to_datetime(df['Data e Ora'])
        
        if not filename:
            filename = f"exports/diario_{start_date}_to_{end_date}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Diario Alimentare', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Diario Alimentare']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4CAF50',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column('A:A', 8)
            worksheet.set_column('B:B', 10)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 50)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:F', 20)
        
        return filename
