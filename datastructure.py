from typing import List
from dataclasses import dataclass, asdict, field
from json import dumps

# 문항 생성
@dataclass
class Question : 
    src_crd : {"x0" : None, "y0" : None,"x1" : None,"y1" : None}
    q_id : None
    type : None
    q_content : None
    q_answer : None
    q_text : None
    q_example : None
    q_selections : {"x0" : None, "y0" : None,"x1" : None,"y1" : None}
    keyword : None
    points : None
        
    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return dumps(self.__dict__,ensure_ascii=False)

# 시험
@dataclass
class Test : 
    def __init__(self, t_id, t_name, questions=None) :
        self.t_id = t_id
        self.t_name = t_name
        self.questions = questions
    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return dumps(self.__dict__)

# 답안
@dataclass
class Answer : 
    def __init__(self, q_id, s_answer, score=0) : 
        self.q_id = q_id
        self.s_answer = s_answer
        self.score = score
# 학생
@dataclass
class Student : 
    def __init__(self, s_id, s_name, answers, total_score=0) : 
        self.s_id = s_id
        self.s_name = s_name
        self.answers = answers
        self.total_score = total_score