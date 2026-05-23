from Generator.log_generator import Generator

class FileReader:
    def __init__(self,filepath):
        self.__filepath = filepath
        
    def read_file_lines(self,lines):        
        Generator().Generate_Logs(lines)
        try:
            with open(self.__filepath, 'r', encoding="utf-8",errors="replace") as file:
                yield from file
        except OSError as e:
            print("Error:", e)