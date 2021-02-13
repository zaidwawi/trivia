import os
from flask import (
  Flask,
  request,
  abort,
  jsonify,
  json
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import (
  setup_db,
  Question,
  Category
)

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow 
  '''
  @app.after_request
  def afterRequest(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PATCH, DELETE')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categrories():
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type
    # return category data to view
    return jsonify({
        'success': True,
        'categories': categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_question():

    selection = Question.query.all()
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)

        # get all categories and add to dict
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

        # return data to view
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete(question_id):
    try:
      the_question = Question.query.get(question_id)
      the_question.delete()
      return jsonify({
            "success":True,
             "deleted":question_id
    })
    except:
      return abort(404)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST'])
  def create_questions():
    body = request.get_json()
    x = body

    if not('question' in x and 'answer' in x and 'difficulty' in x and 'category' in x):
      return abort(422)
    
    theQuestion = Question(
      question = body['question'],
      answer = body['answer'],
      difficulty= body['difficulty'],
      category = body['category']
    )
    theQuestion.insert()
    return jsonify({
      "success":True,
      "created":theQuestion.format()
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    

    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term:

      search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'total_questions': len(search_results),
          'current_category': None
        })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_the_question_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      return jsonify({
              'success': True,
              'questions': [question.format() for question in questions],
              'total_questions': len(questions),
              'current_category': category_id
          })
    except:
      abort(404)
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    data = request.get_json()
    category = data['quiz_category']
    previous_questions = data['previous_questions']
    if category['id'] != 0:
      questions = Question.query.filter_by(category=category['id']).all()
    else:
      questions = Question.query.all()
    def get_random_question():
      next_question = random.choice(questions).format()
      return next_question

    next_question = get_random_question()

    used = False
    if next_question['id'] in previous_questions:
      used = True

    while used:
      next_question = random.choice(questions).format()

      if (len(previous_questions) == len(questions)):
        return jsonify({
          'success': True,
          'message': "game over"
          }), 200

    return jsonify({
    'success': True,
    'question': next_question
    })


  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
  
  return app

    