import os
from copy import deepcopy

"""
Script executável em um intérprete Python que permite trabalhar com textos brutos ou abstraídos, usando
os níveis de resolução propostos por Jordan B. Peterson.
"""

DEFAULT_LABEL = "{{editar}}"

def decimal_func(roman):
    value = {"O": 0, "I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    before = "O"
    total = 0
    for algarism in reversed(roman):
        if value[algarism] < value[before]:
            total -= value[algarism]
        else:
            total += value[algarism]
        before = algarism
    return total

def roman(n):
    roman_positional = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX",
                        10: "X", 20: "XX", 30: "XXX", 40: "XL", 50: "L", 60: "LX", 70: "LXX", 80: "LXXX", 90: "XC",
                        100: "C",
                        0: ""}
    return roman_positional[100 * (n // 100)] + roman_positional[10 * ((n % 100) // 10)] + roman_positional[n % 10]

def opentype(file_name, c_or_t = "t", *args, **kwargs):
    """
    Função que retorna, na pasta em que roda o script, um arquivo com o nome especificado pela variável "str"
    e o formato especificado pela variável "c_or_t".
    """
    if c_or_t == "t":
        f = open(os.getcwd() + "\\" + file_name + ".txt", *args, **kwargs)
    else:
        f = open(os.getcwd() + "\\" + file_name + ".concept", *args, **kwargs)
    return f

def split_ponctuation(line, ponctuation):
    phrases = []
    if ponctuation in line:
        for phrase in line.split(ponctuation):
            phrases.append(phrase + ponctuation)
    else:
        phrases.append(line)
    return phrases

def split_phrases(paragraph):
    phrases = []
    for segment1 in split_ponctuation(paragraph, "."):
        for segment2 in split_ponctuation(segment1, "!"):
            for phrase in split_ponctuation(segment2, "?"):
                phrases.append(phrase)
    return phrases

decimal = {roman(n): n for n in range(1,200)}
literal = {}
i = 0
for letter in "abcdefghijklmnopqrstuvxwyz":
    i += 1; decimal[letter] = i; literal[i] = letter

class ResolutionTree():
    """
    Simboliza a estrutura de uma árvore de resolução sem nomes atribuídos a suas camadas
    """
    def __init__(self, file_name, fmt = "t", title = False):
        if fmt == "t":
            self.origin = "t"
            self.brute_lines = self._readtxt(file_name)
        else:
            self.origin = "c"
            self.brute_lines = self._readconcept(file_name)
        self._process(self.brute_lines, title)

    def _readtxt(self, file_name):
        """
        Lê as linhas do arquivo especificado e retorna suas linhas não processadas.
        """
        original_file = opentype(file_name)
        return original_file.readlines()

    def _readconcept(self, file_name):
        """
        Lê o arquivo em formato concept e retorna suas linhas não processadas
        """
        f = opentype(file_name, "c")
        lines = [line for line in f.readlines() if line != "\n"]
        brute_lines = []
        inside_paragraph = False
        paragraph = []
        for line in lines:
            if not line.startswith("$"):
                continue
            if inside_paragraph:
                if not line[1] == "f":
                    inside_paragraph = False
                    brute_lines.append(" ".join(paragraph))
                paragraph.append(line[3:].rstrip())
            if line[1] == "T" or line[1] == "t":
                brute_lines.append(line[3:])
                continue
            if line[1] == "P":
                paragraph = []
                inside_paragraph = True
                continue
        if len(paragraph) > 0:
            brute_lines.append(" ".join(paragraph))
        return brute_lines

    def _process(self, brute_lines, title):
        """
        Processamento e categorização das linhas
        """
        if type(brute_lines) == type((0,0)):
            blines, l2l = brute_lines
        else:
            blines = brute_lines
        section_number = -1
        subsection_number = -1
        paragraph_number = -1
        label = DEFAULT_LABEL
        self.resolution_tree_dict = dict()
        for line in blines:
            if title:
                title = False
                continue
            if line == "\n":
                continue
            line = line.rstrip()
            if line.startswith("#"):
                if line.startswith("##"):
                    subsection_number += 1
                    paragraph_number = -1
                    self.resolution_tree_dict[(section_number, label)][(subsection_number, label)] = {("subtitle",
                                                                                                       label): line}
                    continue
                else:
                    section_number += 1
                    subsection_number = -1
                    self.resolution_tree_dict[(section_number, label)] = {("title", label): line}
                    continue
            # A linha que chegou até aqui é, na verdade, um parágrafo
            paragraph_number += 1
            paragraph = [l.lstrip() for l in split_phrases(line)]
            del paragraph[-1]
            self.resolution_tree_dict[(section_number, label)
                                    ][(subsection_number, label)
                                    ][(paragraph_number, label)] = paragraph

    def writeto(self, file_name, c_or_t = "c"):
        """
        Escreve a árvore de resolução no arquivo especificado, no formato especificado
        """

        #Preparo das linhas a serem escritas
        lines_to_write = []
        if self.origin == "t":
            blines = self.brute_lines
        else:
            if isinstance(self, EssayConcept):
                blines, garbage = self.brute_lines
            else:
                blines = self.brute_lines
        if c_or_t == "t":
            lines_to_write = blines
            fmt = ".txt"
        else:
            fmt = ".concept"
            for section_number, section_label in self.resolution_tree_dict:
                lines_to_write.extend(("",
                                       "$T " + self.resolution_tree_dict[(section_number, section_label)
                                                                       ]["title", DEFAULT_LABEL],
                                      "{}".format(section_label),
                                       "------------------------------------------------------",
                                      ""
                                      )
                                     )
                for subsection_number, subsection_label in self.resolution_tree_dict[(section_number,
                                                                                      section_label)]:
                    if type(subsection_number) != type(1): continue
                    lines_to_write.extend(("",
                                           "$t " + self.resolution_tree_dict[(section_number, section_label)
                                                                           ][(subsection_number, subsection_label)
                                                                           ][("subtitle", DEFAULT_LABEL)],
                                           "{}".format(subsection_label),
                                           "---------------------------",
                                           ""
                    ))
                    for paragraph_number, paragraph_label in self.resolution_tree_dict[(section_number,
                                                                                        section_label)
                                                                                     ][(subsection_number,
                                                                                        subsection_label)]:
                        if type(paragraph_number) != type(1): continue
                        lines_to_write.extend(("",
                                               "$P Parágrafo {}".format(paragraph_number),
                                              "{}".format(paragraph_label),
                                               "",
                                               ))
                        phrases = self.resolution_tree_dict[(section_number, section_label)
                                                          ][(subsection_number, subsection_label)
                                                          ][(paragraph_number, paragraph_label)]
                        for phrase in phrases:
                            lines_to_write.extend(("$f " + phrase,
                                                  ""))

        #Escrita das linhas
        f = open(os.getcwd() + "\\" + file_name + fmt, "w")
        if fmt == ".txt":
            if self.origin == "c":
                lines_to_write = [line + "\n" if line.endswith("\n") else line + "\n\n" for line in lines_to_write]
            f.writelines(lines_to_write)
        else:
            f.writelines([line + "\n" for line in lines_to_write][1:])
        f.close()
        print("file {} sucessfully written". format(file_name + fmt))


class EssayConcept(ResolutionTree):
    """
    Classe que contém o artigo na sua forma conceitualizada
    """
    def __init__(self, file_name, fmt = "c", title = False):
        super().__init__(file_name, fmt, title)

    def _readconcept(self, file_name):
        """
        Lê o arquivo em formato concept e retorna suas linhas não processadas e um dicionário
        que associa a cada nível uma etiqueta
        """
        f = opentype(file_name, "c")
        lines = [line for line in f.readlines() if line != "\n"]
        level_to_label = dict()
        brute_lines = []
        inside_paragraph = False
        paragraph = []
        get_label = False
        section_number = -1
        subsection_number = -1
        paragraph_number = -1
        for line in lines:
            if get_label:
                level_to_label[(section_number, subsection_number, paragraph_number)] = line.rstrip()
                get_label = False
                continue
            if inside_paragraph:
                if not line[1] == "f":
                    inside_paragraph = False
                    brute_lines.append(" ".join(paragraph))
                else:
                    paragraph.append(line[3:].rstrip())
                    continue
            if not line.startswith("$"):
                continue
            if line[1] == "T":
                section_number += 1; paragraph_number = -1; subsection_number = -1
                brute_lines.append(line[3:])
                get_label = True
                continue
            if line[1] == "t":
                subsection_number += 1; paragraph_number = -1
                brute_lines.append(line[3:])
                get_label = True
                continue
            if line[1] == "P":
                paragraph_number += 1
                get_label = True
                paragraph = []
                inside_paragraph = True
                continue
        if len(paragraph) > 0:
            brute_lines.append(" ".join(paragraph))
        return brute_lines, level_to_label

    def _process(self, brute_lines, title):
        super()._process(brute_lines, title)
        if self.origin == "c":
            self._setlabels(brute_lines)

    def _setlabels(self, brute_lines):
        """
        Reconfigura as chaves do dicionário da árvore de resolução, adicionando as etiquetas de cada nível
        """
        garbage, level_to_label = brute_lines
        tree = deepcopy(self.resolution_tree_dict)

        #criando novas etiquetas
        for section_number, section_label in tree:
            self.resolution_tree_dict[(section_number,
                                       level_to_label[(section_number, -1, -1)])
                                     ] = deepcopy(self.resolution_tree_dict[(section_number, section_label)])
            section = deepcopy(self.resolution_tree_dict[(section_number, level_to_label[(section_number, -1, -1)])])
            for subsection_number, subsection_label in section:
                if type(subsection_number) == type(""): continue

                self.resolution_tree_dict[(section_number,
                                           level_to_label[(section_number, -1, -1)])
                                        ][(subsection_number,
                                           level_to_label[(section_number, subsection_number, -1)])
                                         ] = deepcopy(
                                                      section[(subsection_number, subsection_label)])

                subsection = section[(subsection_number, subsection_label)]
                for paragraph_number, paragraph_label in subsection:
                    if type(paragraph_number) == type(""): continue
                    self.resolution_tree_dict[(section_number,
                                               level_to_label[(section_number, -1, -1)])
                                            ][(subsection_number,
                                               level_to_label[(section_number, subsection_number, -1)])
                                            ][(paragraph_number,
                                               level_to_label[(section_number, subsection_number, paragraph_number)])
                                            ] = deepcopy(subsection[(paragraph_number, paragraph_label)])

        #Apagando etiquetas antigas
        tree = deepcopy(self.resolution_tree_dict)
        for section_number, section_label in tree:
            for subsection_number, subsection_label in tree[(section_number, section_label)]:
                if type(subsection_number) == type(""): continue
                for paragraph_number, paragraph_label in tree[(section_number, section_label)
                                                                                 ][(subsection_number,
                                                                                    subsection_label)]:
                    if type(paragraph_number) == type(""): continue
                    if paragraph_label == DEFAULT_LABEL:
                        del self.resolution_tree_dict[(section_number, section_label)
                                                    ][(subsection_number, subsection_label)
                                                    ][(paragraph_number, paragraph_label)]
                if subsection_label == DEFAULT_LABEL:
                    del self.resolution_tree_dict[(section_number, section_label)
                                                ][(subsection_number, subsection_label)]
            if section_label == DEFAULT_LABEL:
                del self.resolution_tree_dict[(section_number, section_label)]

    def writeto(self, file_name, c_or_t="t"):
        super().writeto(file_name, c_or_t)

    def as_level_hierarchy(self):
        lines = []
        for section_number, section_label in self.resolution_tree_dict:
            if type(section_number) is not int: continue
            lines.append("{}. {}\n".format(roman(section_number + 1), section_label))
            for subsection_number, subsection_label in self.resolution_tree_dict[(section_number, section_label)]:
                if type(subsection_number) is not int: continue
                lines.append("    {}. {}\n".format(literal[subsection_number + 1], subsection_label))
                for paragraph_number, paragraph_label in self.resolution_tree_dict[
                       (section_number, section_label)
                     ][(subsection_number, subsection_label)]:
                    if type(paragraph_number) is not int: continue
                    lines.append("        {}. {}\n".format(paragraph_number + 1, paragraph_label))
        return "".join(lines)