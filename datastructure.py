# 문항 생성
class Question : 
    def __init__(self, q_id=None, type=None, q_content=None, q_text=None, q_example=None, q_answer=None, keyword=None, points=None) :
        self.q_id = q_id
        self.type = type
        self.q_content = q_content
        self.q_answer = q_answer
        self.q_text = q_text
        self.q_example = q_example
        self.keyword = keyword
        self.points = points

# 시험
class Test : 
    def __init__(self, t_id, t_name, questions=None) :
        self.t_id = t_id
        self.t_name = t_name
        self.questions = questions

# 답안
class Answer : 
    def __init__(self, q_id, s_answer, score=0) : 
        self.q_id = q_id
        self.s_answer = s_answer
        self.score = score
# 학생
class Student : 
    def __init__(self, s_id, s_name, answers, total_score=0) : 
        self.s_id = s_id
        self.s_name = s_name
        self.answers = answers
        self.total_score = total_score