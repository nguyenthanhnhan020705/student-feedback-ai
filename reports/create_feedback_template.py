"""Create the user-facing Excel input template."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def create_template(path):
    book=Workbook();sheet=book.active;sheet.title='Phản hồi'
    sheet.append(['Nội dung phản hồi'])
    sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    sheet.column_dimensions['A'].width=95
    for cell in sheet[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='245B97')
    # Instructions outside the data grid avoid importing them as student feedback.
    from openpyxl.comments import Comment
    sheet['A1'].comment=Comment('Nhập phản hồi từ ô A2 trở xuống, mỗi hàng một phản hồi. Một ô có thể gồm nhiều câu. Tối đa 500 phản hồi, 5000 ký tự/phản hồi. Giữ tiêu đề ở dòng 1, không gộp ô. Hệ thống tự chọn cột nội dung và tự tạo mã PH001, PH002… khi nhập file.','Student Feedback AI')
    book.save(path);book.close()

if __name__=='__main__':
    create_template(Path(__file__).resolve().parents[1]/'demo_v3/frontend/mau-phan-hoi.xlsx')
