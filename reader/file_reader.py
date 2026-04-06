from Generator.log_generator import Generator

class FileReader:
    def read_file_lines(self,lines):        
        Generator().Generate_Logs(lines)
        try:
            with open("Logs.txt", 'r', encoding="utf-8",errors="replace") as file:
                yield from file
        except OSError as e:
            print("Error:", e)