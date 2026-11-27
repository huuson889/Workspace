"""Optional: regenerate the bundled non-private examples (python-docx/python-pptx)."""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.util import Inches as PI, Pt as PP
from pptx.dml.color import RGBColor as PC
from pptx.enum.shapes import MSO_SHAPE

root = Path(__file__).resolve().parents[1] / 'public' / 'samples'
root.mkdir(parents=True, exist_ok=True)
d = Document()
section = d.sections[0]
section.header.paragraphs[0].text = 'KEEPIT / OFFICE → PDF LAB'
normal = d.styles['Normal']
normal.font.name = 'Carlito'
normal.font.size = Pt(12)
normal.font.color.rgb = RGBColor.from_string('243C40')
d.add_heading('Một tài liệu, một trải nghiệm đọc.', 0)
d.add_paragraph('DOCX → LibreOffice → PDF.js', 'Subtitle')
d.add_paragraph('Đây là tài liệu mẫu tạo riêng cho bản thử Keepit. Nội dung này được LibreOffice chuyển thật thành PDF; không phải ảnh chụp hay kết quả dựng sẵn.')
d.add_heading('01 / Kiểm tra lớp chữ', 1)
d.add_paragraph('Bạn có thể kéo chọn dòng này: Tiếng Việt có dấu — học tập, ghi chú và khám phá.')
d.add_paragraph('English text: Keep your ideas in one place. Select this sentence to inspect the real PDF text layer.')
d.add_heading('02 / Bảng và định dạng', 1)
table = d.add_table(rows=1, cols=3)
table.style = 'Light Shading Accent 1'
for c, text in zip(table.rows[0].cells, ['Đầu vào', 'Bộ chuyển đổi', 'Đầu ra']):
    c.text = text
for values in [('DOCX', 'LibreOffice Writer', 'PDF có lớp chữ'), ('PPTX', 'LibreOffice Impress', 'Slide tĩnh dạng PDF')]:
    for c, text in zip(table.add_row().cells, values):
        c.text = text
d.add_paragraph('Mẫu này có hai trang cố định bằng ngắt trang. Tệp DOCX khác có thể phân trang khác khi thiếu phông chữ.')
d.add_page_break()
d.add_heading('Trang 2 / Đọc, chọn và tải PDF', 0)
d.add_paragraph('Nếu bạn đang nhìn thấy trang này, luồng chuyển đổi nhiều trang đã hoạt động.')
for text in ['Dùng mũi tên hoặc ô số trang để điều hướng.', 'Đổi thu phóng để kiểm tra độ nét.', 'Tải bản PDF hoặc xóa phiên trên máy chủ.']:
    d.add_paragraph(text, style='List Bullet')
d.add_heading('Lưu ý về độ trung thực', 1)
d.add_paragraph('LibreOffice có thể thay phông hoặc bố cục so với Microsoft Office. Đây là bản thử chức năng, không phải cam kết mọi tài liệu sẽ giống bản gốc tuyệt đối.')
section.footer.paragraphs[0].text = 'Keepit · Demo document · No private content'
d.save(root / 'keepit-sample.docx')

r = Presentation()
r.slide_width = PI(13.333)
r.slide_height = PI(7.5)
for i in range(2):
    s = r.slides.add_slide(r.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = PC.from_string('EDF4EF' if i == 0 else '163F35')
    dark = i == 1
    def text(x, y, w, h, value, size, color, bold=False):
        box = s.shapes.add_textbox(PI(x), PI(y), PI(w), PI(h))
        p = box.text_frame.paragraphs[0]
        p.text = value
        p.font.name = 'Carlito'
        p.font.size = PP(size)
        p.font.bold = bold
        p.font.color.rgb = PC.from_string(color)
    text(.8,.5,10,.4,'KEEPIT / PRESENTATION SAMPLE',12,'8BA397' if dark else '4C7C69',True)
    text(.8,1.5,10,1.6,'Từ slide Office\nđến trải nghiệm PDF.' if i == 0 else 'Chữ thật.\nKhông chỉ là ảnh.',40,'FFFFFF' if dark else '163F35',True)
    text(.85,4,9,1,'PPTX → LibreOffice → PDF.js' if i == 0 else 'Bạn có thể chọn dòng này: Tiếng Việt có dấu.',20,'C8DBD1' if dark else '517366')
    for j in range(3):
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,PI(.85+j*3.9),PI(5.5),PI(3.55),PI(.9))
        sh.fill.solid(); sh.fill.fore_color.rgb=PC.from_string('285648' if dark else 'FFFFFF')
        sh.line.fill.background()
        tf=sh.text_frame;tf.paragraphs[0].text=['01  Mở tài liệu','02  Chuyển thành PDF','03  Đọc & chọn chữ'][j]
        tf.paragraphs[0].font.name='Carlito';tf.paragraphs[0].font.size=PP(16)
        tf.paragraphs[0].font.color.rgb=PC.from_string('FFFFFF' if dark else '226D5B')
    text(11.7,.6,.8,.4,f'0{i+1}',12,'8BA397' if dark else '4C7C69')
r.save(root / 'keepit-sample.pptx')
print('Generated', list(root.iterdir()))
