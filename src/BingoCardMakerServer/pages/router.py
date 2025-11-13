"""
Router for the pages modual that generates and returns the various html files and pages
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .. import constants
from ..admintools.sitesettings import site_settings

router = APIRouter(
	prefix="",
	tags=["pages"],
)


templates = Jinja2Templates(directory=constants.TEMPLATE_DIR)

root_template_context={
	"domain_url": site_settings.site_url,
	"page_title": site_settings.site_title,
	"banner_title": "The Bingo Card Generator",
	"description": "This is the default description",
}

@router.get("/", response_class=HTMLResponse)
async def generate_homepage_response(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="index.html",
		context=root_template_context
	)

@router.get("/login", response_class=HTMLResponse)
async def generate_login_response(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="login.html",
		context=root_template_context
	)

@router.get("/editcardconfig", response_class=HTMLResponse)
async def get_editcardconfig(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="cardconfig.html",
		context=root_template_context
	)

@router.get("/uploadimage", response_class=HTMLResponse)
async def get_uploadimage(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="uploadimage.html",
		context=root_template_context
	)

