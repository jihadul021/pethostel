# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q

# Python standard library imports
import io
from datetime import date, datetime

# Local app imports
from .forms import EmployeeForm, PetForm
from .models import EmployeeReg, PetRegistration, UserProfile, Room, Booking

# ReportLab imports for PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


def home(request):
        pets = PetRegistration.objects.filter(owner_id=request.user.id)
        return render(request, 'home.html',{'pets':pets})

def services(request):
    return render(request, 'services.html')

@login_required
def add_room(request):
    if request.method=='POST':
        type = request.POST['category']
        count = int(request.POST['count'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.total_rooms += count
            r.save()
        return redirect('room')

    return render(request,'add_room.html')

@login_required
def remove_room(request):
    if request.method=='POST':
        type = request.POST['category']
        count = int(request.POST['count'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.total_rooms -= count
            r.save()
        return redirect('room')
    return render(request,'remove_room.html')

@login_required
def room_info(request):
    room = Room.objects.all()
    bookings = Booking.objects.all()
    return render(request,'room.html',{'room':room, 'bookings':bookings})

@login_required
def pricechange(request):
    if request.method=='POST':
        type = request.POST['category']
        new_price = int(request.POST['price'])
        room = Room.objects.filter(category=type)
        for r in room:
            r.price = new_price
            r.save()
        return redirect('room')
    return render(request,'price_change.html')
#=============authentication part===============

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return render(request, 'login.html')
    elif request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

#-------------------Employees-------------------
@login_required
def employee_list(request):
      employees = EmployeeReg.objects.all()
      return render(request, 'employee_list.html',{'employees':employees})

@login_required
def employee_add(request):
        if request.method == 'POST':
            form = EmployeeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('employee_list')
        else:
            form = EmployeeForm
        return render(request, 'employee_add.html', {'form': form})

@login_required
def remove_employee(request, employee_id):
    employee = EmployeeReg.objects.get(pk=employee_id)
    employee.is_active = False
    employee.save()
    return redirect('employee_list')

#================Customers===============

def register(request):
    if request.method == 'POST':
        fname = request.POST ['fname']
        lname = request.POST ['lname']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST ['phone']
        birth = request.POST ['birth']
        address = request.POST ['address']
        password = request.POST['passwrd']
        if User.objects.filter(username=username).exists():
            messages.info(request,'Usrname already in use')
            return render(request,'register.html')
        else:
            user = User.objects.create_user(first_name = fname, last_name = lname, email=email,password=password,username=username)
            profile = UserProfile.objects.create(user=user, phone_number=phone, birthdate=birth, address=address)

            #login
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('/')

    elif request.user.is_authenticated:
        return redirect('/')
    return render(request,'register.html')

@login_required
def customers(request):
    users = User.objects.select_related('userprofile').all()
    pets = PetRegistration.objects.all()
    bookings = Booking.objects.all()
    return render(request,'customers.html', {'users':users, 'pets':pets, 'bookings':bookings})

@login_required
def pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('/')
    else:
        form = PetForm
    return render(request,'petregister.html',{'form':form})

#=======management==============
def search(request):
    return render(request,'search.html')

@login_required
def confirm_booking(request):
    if request.method == 'POST':
        checkin = request.POST['checkin']
        checkout = request.POST['checkout']
        petcount = int(request.POST['petcount'])
        category = request.POST['category']
        cost = request.POST['cost']
        pets = request.POST.getlist('pets')
        if len(pets)>petcount:
            messages.info(request, 'You used invalid pet numbers, Please try again')
            return redirect('search')

    booking =  Booking.objects.create(check_in_date=checkin, check_out_date=checkout, number_of_pets=petcount, room_category = category, cost=cost,  customer=request.user, pets=pets)
    booking.save()
    return redirect('booking_success', booking_id=booking.id)

def availability(request):
    if request.method=='POST':
        available = True
        checkin = request.POST['check_in']
        checkout = request.POST['check_out']
        petnumber = int(request.POST['pet_number'])
        category = request.POST['room_type']

      #====booking dates validity check======
        if checkout<checkin or checkin<str(date.today()):
            messages.info(request, 'Invalid date input')
            return redirect('search')

        booked_rooms = Booking.objects.filter(room_category=category)
        categ = Room.objects.filter(category=category)
        room_price = 0

        #if booked room exist for same category
        if booked_rooms:
            total_pets = 0
            overlapping_bookings = Booking.objects.filter(Q(check_in_date__lte=checkout, check_out_date__gte=checkin, room_category=category))
            if overlapping_bookings.exists():
                for i in overlapping_bookings:
                    total_pets += i.number_of_pets
            for r in categ:
                if total_pets + petnumber <= (r.capacity * r.total_rooms):
                    pass
                else:
                    available = False
    #============end of existing bookings==============
        if available:
            # duration and price calculation
            day_count = int(checkout[-2:])-int(checkin[-2:])+1
            month_count = int(checkout[-5:-3])-int(checkin[-5:-3])
            year_count =  int(checkout[:4])-int(checkin[0:4])
            if year_count>0:
                month_count += 12 * year_count

            if month_count>0 and day_count>0:
                day_count += month_count * 30
            elif month_count>0 and day_count<0:
                day_count = ((month_count-1)*30) + (30+day_count)

            if categ.exists():
                room = categ.first()
                room_price = room.price * petnumber * day_count


            context = {
                'checkin':checkin,
                'checkout':checkout,
                'petcount':petnumber,
                'category':category,
                'pets': PetRegistration.objects.filter(owner_id = request.user.id),
                'cost': room_price,
            }

            return render(request,'booking.html',context)
        else:
            messages.info(request,'Not available, Please try a different category or date')
            return redirect('search')

@login_required
def bookinglist(request):
    bookings = Booking.objects.order_by('-id')
    return render(request, 'booking_info.html',{'bookings':bookings})

@login_required
def booking_success(request, booking_id):
    """Display booking success page"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    return render(request, 'success.html', {'booking': booking})

@login_required
def download_receipt(request, booking_id):
    """Generate and download PDF receipt"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Pet_Hostel_Receipt_{booking.id}.pdf"'

    # Create the PDF object, using the response object as its "file"
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#667eea')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#333333')
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 12

    # Add title
    title = Paragraph("🏨 Pet Hostel - Booking Receipt", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Add booking info header
    booking_header = Paragraph("Booking Confirmation", heading_style)
    elements.append(booking_header)
    elements.append(Spacer(1, 10))

    # Customer and booking details
    customer_info = [
        ['Customer Name:', f"{booking.customer.first_name} {booking.customer.last_name}"],
        ['Email:', booking.customer.email],
        ['Phone:', getattr(booking.customer.userprofile, 'phone_number', 'N/A') if hasattr(booking.customer, 'userprofile') else 'N/A'],
        ['Booking Date:', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ['Booking ID:', f"#{booking.id}"],
    ]

    customer_table = Table(customer_info, colWidths=[2*inch, 3*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9ff')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#fafbff')])
    ]))

    elements.append(customer_table)
    elements.append(Spacer(1, 30))

    # Booking details header
    booking_details_header = Paragraph("Reservation Details", heading_style)
    elements.append(booking_details_header)
    elements.append(Spacer(1, 10))

    # Calculate duration safely
    duration = 1 + ((booking.check_out_date - booking.check_in_date).days)
    cost_per_night = booking.cost // duration

    # Booking details table
    booking_details = [
        ['Check-in Date:', booking.check_in_date.strftime('%Y-%m-%d')],
        ['Check-out Date:', booking.check_out_date.strftime('%Y-%m-%d')],
        ['Duration:', f"{duration} night{'s' if duration != 1 else ''}"],
        ['Room Category:', booking.room_category.title()],
        ['Number of Pets:', str(booking.number_of_pets)],
        ['Cost per Night:', f"TK {cost_per_night}"],
        ['Payment Status:', f"UNPAID"],
    ]

    booking_table = Table(booking_details, colWidths=[2*inch, 3*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e8')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#fafbff')])
    ]))

    elements.append(booking_table)
    elements.append(Spacer(1, 30))

    # Total cost section
    total_data = [
        ['', 'TOTAL AMOUNT:', f"TK {booking.cost}"]
    ]

    total_table = Table(total_data, colWidths=[2*inch, 2*inch, 1*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (-1, -1), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (1, 0), (-1, -1), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (1, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (-1, -1), 14),
        ('GRID', (1, 0), (-1, -1), 2, colors.HexColor('#45a049'))
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 40))

    # Footer information
    footer_info = Paragraph(
        "<b>Pet Hostel Contact Information:</b><br/>"
        "📞 Phone: 017000000000<br/>"
        "📧 Email: info@pethostel.com<br/>"
        "📍 Address: H12, Central Road, Dhanmondi, Dhaka<br/><br/>"
        "<i>Thank you for choosing Pet Hostel - Your pet's second home!</i>",
        normal_style
    )
    elements.append(footer_info)

    # Build PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response