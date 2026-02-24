from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def export_full_docx(data_list, start_time, end_time, filename="detailed_report.docx"):
    """
    适配后端的导出函数
    :param data_list: 数据库查询出的字典列表
    :param start_time: 前端传来的开始时间字符串
    :param end_time: 前端传来的结束时间字符串
    :param filename: 生成的临时文件名
    """
    doc = Document()
    
    # 1. 标题与范围声明
    title = doc.add_heading('设备全参数运行日志详细报告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    info_para = doc.add_paragraph()
    info_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info_para.add_run(f"统计周期：{start_time} 至 {end_time}")
    run.font.size = Pt(11)
    
    if not data_list:
        doc.add_paragraph("\n查询时间范围内无记录。")
        doc.save(filename)
        return filename

    # 2. 定义字段逻辑分组 (可根据实际需求增减)
    sections = {
        "1. 基本信息与系统状态": [
            ('timestamp', '记录时间'), ('sys_mode', '工作模式'), 
            ('sys_signal_source', '信号源'), ('sys_lock_status', '锁定状态'),
            ('sys_lock_indicator', '锁定指示')
        ],
        "2. 信号详细参数": [
            ('sig_agc_threshold', 'AGC门限'), ('sig_agc_voltage', 'AGC电压'),
            ('sig_azimuth_err_v', '方位误差电压'), ('sig_pitch_err_v', '俯仰误差电压')
        ],
        "3. 转台系跟踪数据": [
            ('tt_guide_az', '引导方位'), ('tt_curr_az', '当前方位'), ('tt_dev_az', '方位偏差'),
            ('tt_guide_pt', '引导俯仰'), ('tt_curr_pt', '当前俯仰'), ('tt_dev_pt', '俯仰偏差')
        ],
        "4. 电机诊断数据": [
            ('m1_status', '电机1状态'), ('m1_temp', '电机1温度'), ('m1_current', '电机1电流'),
            ('m2_status', '电机2状态'), ('m2_temp', '电机2温度'), ('m2_current', '电机2电流')
        ]
    }

    # 3. 循环生成内容
    for index, record in enumerate(data_list):
        # 每一条数据的大标题
        doc.add_heading(f"记录 #{index + 1} | 录入时间: {record.get('timestamp')}", level=1)
        
        for section_name, fields in sections.items():
            doc.add_heading(section_name, level=2)
            
            # 创建 2 列的窄表（Key-Value 模式）
            table = doc.add_table(rows=0, cols=2)
            table.style = 'Table Grid'
            table.autofit = False 
            
            for key, label in fields:
                row_cells = table.add_row().cells
                # 第一列：参数名（加粗，固定宽度）
                row_cells[0].width = Inches(1.8)
                row_cells[0].text = label
                row_cells[0].paragraphs[0].runs[0].font.bold = True
                
                # 第二列：具体数值
                raw_val = record.get(key)
                val = str(raw_val) if raw_val is not None else "N/A"
                row_cells[1].text = val
                
                # 针对温度的阈值报警（红色高亮）
                if "temp" in key:
                    try:
                        if float(val) > 50:
                            run = row_cells[1].paragraphs[0].runs[0]
                            run.font.color.rgb = RGBColor(200, 0, 0)
                            run.font.bold = True
                    except:
                        pass
            
            doc.add_paragraph() # 段落间距

        # 每条记录占一页或多页，最后一条不加分页符
        if index < len(data_list) - 1:
            doc.add_page_break()

    # 4. 保存
    doc.save(filename)
    return filename