import PyPDF2
import argparse
import copy
import os
import time
from multiprocessing import Pool

start = time.time()


def slice_pdf(file_name: str) -> None:
    """
    Slice the pdf's pages into 4 and insert them into a new page in a new document.
    :param file_name: The filename of the pdf's file that will be sliced.
    """

    output = PyPDF2.PdfFileWriter()
    print("-- Reading file: " + file_name)
    pdf_file = PyPDF2.PdfFileReader(open(file_name, "rb"))
    print("--- File read")

    print("--- Starting looping and slicing pdf")

    # These are the attributes the mediaBox object has which we need to change to apply slicing
    page_elements = ["lowerRight", "lowerLeft", "upperRight", "upperLeft"]
    for x in range(0, pdf_file.getNumPages() - 1):
        for index in range(len(page_elements)):
            # Copy by value is needed because the reference is directly changed
            page = copy.copy(pdf_file.getPage(x))

            # Override the point where the page ends to apply the slicing
            setattr(page.mediaBox, page_elements[index], (
                page.mediaBox.getUpperRight_x() / 2,
                page.mediaBox.getUpperRight_y() / 2
            ))
            # Revert scaling to what is was before slicing
            page.scaleBy(2)
            output.addPage(page)

    print("--- Ending looping and slicing pdf")

    # Remove the .pdf from the filename and insert -output.pdf
    os.makedirs("build", exist_ok=True)
    print("--- Writing file: " + file_name)
    output_stream = open("build/" + file_name[:-4] + "-output.pdf", "wb")
    output.write(output_stream)
    print("--- Write successful for file: " + file_name)


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-d', "--directory", help='Specify a directory to find pdf files from')
group.add_argument('-f', '--file', help='Specify a file to slice.')
args = parser.parse_args()

if args.directory is not None:
    pool = Pool()
    files = [f for f in os.listdir(args.directory) if not (not os.path.isfile(f) or not f.endswith('.pdf') or f.endswith('-output.pdf'))]
    # run through the files asynchronously
    pool.map(slice_pdf, files)

if args.file is not None:
    slice_pdf(args.file)

end = time.time()
print('Time taken: ', (end - start), ' seconds')
