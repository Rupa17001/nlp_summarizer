import os
from PyPDF2 import PdfReader, PdfWriter


def split_pdf_folder(folder_name):
    # Create a directory to store the output files
    print("splitting files")
    output_dir = folder_name + '_split'
    os.makedirs(output_dir, exist_ok=True)

    # Get a list of PDF files in the input folder
    pdf_files = [file for file in os.listdir(folder_name) if file.lower().endswith('.pdf')]

    # Split each PDF file into chunks
    for pdf_file in pdf_files:
        filename = os.path.join(folder_name, pdf_file)
        with open(filename, 'rb') as file:
            pdf = PdfReader(file)
            total_pages = len(pdf.pages)

            # Determine the number of chunks
            num_chunks = total_pages // 2
            if total_pages % 1 != 0:
                num_chunks += 1

            # Split the PDF into chunks
            for i in range(num_chunks):
                start_page = i * 1
                end_page = min((i + 1) * 1, total_pages)
                output_pdf = PdfWriter()

                # Add pages to the output PDF
                for page_num in range(start_page, end_page):
                    output_pdf.add_page(pdf.pages[page_num])

                # Save the output PDF as a new file
                    output_filename = os.path.join(output_dir, f'{os.path.splitext(pdf_file)[0]}_{i+1}.pdf')
                    with open(output_filename, 'wb') as output_file:
                        output_pdf.write(output_file)

    return os.path.abspath(output_dir)