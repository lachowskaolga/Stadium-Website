from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponse
import csv
from django.contrib import messages
#Import PDF stuff
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
#Import Paginator Stuff
from django.core.paginator import Paginator


def show_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, 'events/show_event.html', {
        "event": event,
    })

def venue_events(request, venue_id):
    venue = Venue.objects.get(id=venue_id)

    events = venue.event_set.all()
    if events:
        return render(request, 'events/venue_events.html', {
            "events": events,
        })
    else:
        messages.success(request, ("That venue has no events."))			
        return redirect('admin_approval')


def admin_approval(request):
	#get venues:
	venue_list = Venue.objects.all()

	event_count = Event.objects.all().count()
	venue_count = Venue.objects.all().count()
	user_count = User.objects.all().count()

	event_list = Event.objects.all().order_by("-event_date")
	if request.user.is_superuser:
		if request.method == "POST":
			id_list = request.POST.getlist('boxes')

			#uncheck all events
			event_list.update(approved=False)


			#update database:
			for x in id_list:
				Event.objects.filter(pk=int(x)).update(approved=True)

			messages.success(request, ("Event List Approval has been updated."))			
			return redirect('list-events')
		else:
			return render(request, 'events/admin_approval.html', {
				"event_list":event_list,
				"event_count":event_count,
				"venue_count":venue_count,
				"user_count":user_count,
				"venue_list":venue_list,
				})
	else:
		messages.success(request, ("You aren't authorized to view this page."))
		return redirect(request, 'home')

	return render(request, 'events/admin_approval.html', {})


def my_events(request):
	if request.user.is_authenticated:
		me = request.user.id
		events = Event.objects.filter(attendees=me)
		return render(request, 'events/my_events.html', {
			"events":events,
			})

	else:
		messages.success(request, ("You aren't authorized to view this page."))
		return redirect('home')

# Generate a PDF file Venue List:
def venue_pdf(request):
    #create bytestream buffer:
    buf = io.BytesIO()
    #Create Canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    #Create a text object:
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Designate The Model
    venues = Venue.objects.all()
    #Create blank list
    lines = []
 
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.adress)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_adress)
        lines.append("---------------------------")

    for line in lines:
        textob.textLine(line)

    #Finish Up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    #return something:
    return FileResponse(buf, as_attachment=True, filename="venue.pdf")


#Generate Text file venue list:
def venue_text(request):
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition']='attachment; filename=venues.txt'
	#Designate The Model
	venues=Venue.objects.all()
	lines = []
	#Loop Thu and output
	for venue in venues:
		lines.append(f'{venue.name}\n{venue.adress}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_adress}\n\n')

	#Write to TextFile:
	response.writelines(lines)
	return response


def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    # Create csv writer
    writer = csv.writer(response)

    # Designate The Model
    venues = Venue.objects.all()

    # Add column headings to file:
    writer.writerow(['Venue Name', 'Adress', 'Zip Code', 'Phone', 'Web Adress', 'Email'])

    # Loop through venues and output each venue on a separate row
    for venue in venues:
        writer.writerow([venue.name, venue.adress, venue.zip_code, venue.phone, venue.web, venue.email_adress])

    return response


def delete_event(request, event_id):
	event = Event.objects.get(pk=event_id)
	if request.user ==event.manager:
		event.delete()
		messages.success(request, ("Event deleted!"))
		return redirect('list-events')
	else:
		messages.success(request, ("You are not authorized to delete this event!"))	
		return redirect('list-events')


def delete_venue(request, venue_id):
	venue = Venue.objects.get(pk=venue_id)
	venue.delete()
	return redirect('list-venues')


def add_event(request):
	submitted = False
	if request.method == 'POST':
		if request.user.is_superuser:
			form = EventFormAdmin(request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect("/add_event?submitted=True")
		else:
			form=EventFormAdmin(request.POST)
			if form.is_valid():
				event = form.save(commit=False)
				event.manager = request.user
				event.save()
				return HttpResponseRedirect("/add_event?submitted=True")
	
	else:
		if request.user.is_superuser:
			form = EventFormAdmin
		else:
			form = EventForm

		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'events/add_event.html', {
		"form":form,
		"submitted":submitted,
		})


def edit_event(request, event_id):
	event = Event.objects.get(pk=event_id)
	if request.user.is_superuser:
		form = EventFormAdmin(request.POST or None, instance=event)
	else:
		form = EventForm(request.POST or None, instance=event)		
	
	if form.is_valid():
		form.save()
		return redirect('list-events')
	
	return render(request, 'events/edit_event.html',{
		"event":event,
		"form":form,
		})	


def update_venue(request, venue_id):
	venue = Venue.objects.get(pk=venue_id)
	form = VenueForm(request.POST or None,  request.FILES or None,instance=venue)
	if form.is_valid():
		form.save()
		return redirect('list-venues')

	return render(request, 'events/update_venue.html',{
		"venue":venue,
		"form":form,
		})	


def search_venues(request):
	if request.method=="POST":
		searched = request.POST['searched']
		venues = Venue.objects.filter(name__contains=searched)
		return render(request, 'events/search_venues.html',{
			'searched':searched,
			'venues':venues,
			})	
	else:
		return render(request, 'events/show_venue.html',{

		})

def search_events(request):
	if request.method=="POST":
		searched = request.POST['searched']
		events = Event.objects.filter(description__contains=searched)
		return render(request, 'events/search_events.html',{
			'searched':searched,
			'events':events,
			})	
	else:
		return render(request, 'events/search_events.html',{
		})

def show_venue(request, venue_id):
	venue = Venue.objects.get(pk=venue_id)
	venue_owner = User.objects.get(pk=venue.owner)
	return render(request, 'events/show_venue.html',{
		"venue":venue,
		"venue_owner":venue_owner,
		})


def list_venues(request):
	#venue_list = Venue.objects.all().order_by('?')
	venue_list = Venue.objects.all()
	#Set up pagination
	p = Paginator(Venue.objects.all(), 7) #po 3 na stronie się wyświetlą
	page = request.GET.get('page')
	venues = p.get_page(page)

	return render(request, 'events/venue.html', {
		"venue_list":venue_list,
		"venues":venues,
		})

def add_venue(request):
	submitted = False
	if request.method == 'POST':
		form = VenueForm(request.POST, request.FILES)
		if form.is_valid():
			venue = form.save(commit=False)
			venue.owner = request.user.id #logged in user
			venue.save()
			#form.save()
			return HttpResponseRedirect("/add_venue?submitted=True")
	else:
		form = VenueForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'events/add_venue.html', {
		"form":form,
		"submitted":submitted,
		})



def all_events(request):
	event_list = Event.objects.all().order_by('-event_date')

	return render(request, 'events/event_list.html',{
		"event_list":event_list,
		})




def home (request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	name = "Olga"
	month = month.capitalize()
	#Convert month from name to number
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	#create calendar:
	cal =HTMLCalendar().formatmonth(
		year, 
		month_number)

	#Get current year
	now=datetime.now()
	current_year=now.year
	#current time:
	time=now.strftime('%H:%M:%S')


	return render(request, 'events/home.html', {
		"name":name,
		"year":year,
		"month":month,
		"month_number":month_number,
		"cal":cal,
		"current_year":current_year,
		"time":time
		})


