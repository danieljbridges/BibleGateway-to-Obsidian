import os
import pandas as pd
import subprocess
import re

base_dir = os.getcwd()
version = "NIV"
output_dir = os.path.join(base_dir, version) 

def main():
    #Pull in all book of the Bible
    books_df = pd.read_csv(os.path.join(base_dir,"Bible_books.csv"))
    
    #Define Bible index file
    bible_index = []
    bible_indexmd = f"{version}.md"
    bible_indexmdpath = os.path.join(base_dir, version, bible_indexmd)
    
    print(f"Starting process to download {version} Bible.")
    
    #for each row in the df pull out the row and split into the diff outputs
    for index, row in books_df.iterrows():
        book_indexfullnm = f"{str(index + 1).zfill(2)} - {row[0]}"
        book_fullnm = row[0]
        book_shortnm = row[1]
        book_abbrnm = row[2]
        book_chapter_count = row[3]
        book_dir = os.path.join(output_dir, book_indexfullnm)
        
        print(f"{book_indexfullnm}")

        #Create folder if needed
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)

        book_chapters = []
        book_index_mdpath = os.path.join(book_dir, f"{book_fullnm} {version}.md")
        
        for chapter_num in range(1, book_chapter_count +1, 1):
            chapter_numpad = str(chapter_num).zfill(2)
            chapter_numpadplus = str(chapter_num+1).zfill(2)
            chapter_numpadminus = str(chapter_num-1).zfill(2)
            chapter_title = f"{book_fullnm} {str(chapter_numpad)} {version}"
            chapter_mdpath = os.path.join(book_dir, chapter_title + ".md")
            #Download and format chapter if not present
            if not os.path.exists(chapter_mdpath):
                #Deal with first chapters 
                if chapter_num == 1:
                    prev_chapter = ""
                else:
                    prev_chapter = f"[[{book_fullnm} {chapter_numpadminus} {version}|←Chapter {chapter_num-1}]]|"
                #Deal with last chapters
                if chapter_num == book_chapter_count :
                    next_chapter = ""
                else:
                    next_chapter = f"|[[{book_fullnm} {chapter_numpadplus} {version}|Chapter {chapter_num+1}→]]"

                #Build markdown file components 
                chapter_links = f"{prev_chapter}[[{book_fullnm} {version}|{book_fullnm}]]{next_chapter}\n"
                chapter_YAML = f"---\ntag: \"#type/book/Bible\"\nalias: {book_abbrnm}{chapter_numpad}_{version}\nbible_translation: {version}\nbible_book: {book_fullnm}\nbible_chapter: {book_shortnm}{chapter_numpad}\n---"
                chapter_header = f"{chapter_YAML}\n# {chapter_title}\n"
                
                print(f"      {book_shortnm} {chapter_num} downloading")
                
                chapter_downloaded = subprocess.run(['ruby', 'bg2md.rb', '-cflre', f'-v {version}', f'{book_fullnm} {chapter_num}'], 
                                                    stdout=subprocess.PIPE, text=True)

                chapter_verses = "".join([ re.sub(r"^###### (\d+) (.+)", r"###### \1\n\2", line) for line in chapter_downloaded.stdout.splitlines(True) 
                                  if line.startswith("######")])
                
                # Output to file
                with open(chapter_mdpath, "w") as mdfile:
                    mdfile.write(chapter_header)
                    mdfile.write(chapter_links)
                    mdfile.write(chapter_verses)
                    mdfile.write(chapter_links)

            #Create an index for the book
            book_chapters.append(f"[[{chapter_title}|Chapter {str(chapter_num)}]]")

            #Create index when reached the last chapter
            if chapter_num == book_chapter_count:
                book_YAML = f"---\ntag: \"#type/book/Bible\"\nalias: {book_abbrnm}_index\nbible_translation: {version}\nbible_book: {book_fullnm}\n---"
                book_header = f"{book_YAML}\n# {book_fullnm}\n[[{bible_indexmd}|{version} Index]]\n"
                
                print("      Outputting book index")
                with open(book_index_mdpath, "w") as mdfile:    
                    mdfile.write((book_header))
                    mdfile.write(", ".join(book_chapters))
        
        #Create an reference for the book in the master
        bible_index.append(f"[[{book_fullnm} {version}.md|{book_fullnm}]]")
        # if index ==  0:
        #     break

    print("   Outputting Bible index")
    bibleindex_YAML = f"---\ntag: \"#type/book/Bible\"\nalias: {version}_index\nbible_translation: {version}\n---"
    bibleindex_header = f"{bibleindex_YAML}\n# {version}\n"
                
    with open(bible_indexmdpath, "w") as mdfile:
        mdfile.write((bibleindex_header))
        mdfile.write("\n".join(bible_index))
    
if __name__ == "__main__" :
    main()