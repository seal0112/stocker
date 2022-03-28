from flask import Blueprint
from flask_restx import Api
from app.doc.basicInfo import namespace as basicInfo_ns
from app.doc.dailyInfo import namespace as dailyInfo_ns
from app.doc.incomeSheet import namespace as incomeSheet_ns
from app.doc.monthRevenue import namespace as monthRevenue_ns

blueprint = Blueprint('doc', __name__)

api_extension = Api(
    blueprint,
    title = 'Stocker API Documentation',
    version = '0.0',
    # description = 'Stocker RESTful API Documetation',
    doc = '/v0'
)

api_extension.add_namespace(basicInfo_ns)
api_extension.add_namespace(dailyInfo_ns)
api_extension.add_namespace(incomeSheet_ns)
api_extension.add_namespace(monthRevenue_ns)