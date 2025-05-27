
# from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum





from .models import Worker, Attendance , ActivityLog
from django.utils import timezone
from django.db import IntegrityError


from django.views.decorators.http import require_POST

from datetime import datetime
from django.utils import timezone



from django.utils.timezone import now
from django.db.models import Count, Q
import datetime

def home(request):
    return render(request, 'worker/home.html')




def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'worker/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')






@login_required
def dashboard(request):

    


    if request.method == 'POST':
        if 'add_worker' in request.POST:
            name = request.POST['name']
            worker_type = request.POST['worker_type']
            daily_salary = int(request.POST['daily_salary'])
            date_of_joining = request.POST['date_of_joining']

            Worker.objects.create(
                name=name,
                worker_type=worker_type,
                daily_salary=daily_salary,
                date_of_joining=date_of_joining
            )

        elif 'mark_attendance' in request.POST:
            worker_id = request.POST['worker_id']
            worker = Worker.objects.get(id=worker_id)
            try:
                Attendance.objects.create(worker=worker, date=timezone.now().date())
            except IntegrityError:
                pass  # already marked

        return redirect('dashboard')

    # ==== Data Calculation ====
    workers = Worker.objects.all()
    total_workers = workers.count()
    today = timezone.now().date()

    # Get today's attendance count
    present_today_count = Attendance.objects.filter(date=today).count()

    # Optional: total monthly salary so far
    current_month = today.month
    current_year = today.year
    total_month_salary = Attendance.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('worker__daily_salary'))['total'] or 0

   

    return render(request, 'worker/dashboard.html',  {
        'workers': workers,
        'today_attendance': Attendance.objects.filter(date=today).values_list('worker_id', flat=True),
        'today': today,
        'total_workers': total_workers,
        'present_today_count': present_today_count,
        'total_month_salary': total_month_salary,
         


        
    })




def add_delete_worker_view(request):
    if request.method == "POST" and 'name' in request.POST:
        Worker.objects.create(
            name=request.POST['name'],
            worker_type=request.POST['worker_type'],
            daily_salary=request.POST['daily_salary']
        )
        return redirect('add_worker')
    
    workers = Worker.objects.all()
    return render(request, 'worker/add_delete_worker.html', {'workers': workers})

@require_POST
def delete_worker_view(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)
    worker.delete()
    return redirect('add_worker')









def mark_attendance_view(request):
    today = request.POST.get('date') or timezone.now().date()

    # Ensure 'today' is a date object
    if isinstance(today, str):
        # today = datetime.strptime(today, "%Y-%m-%d").date()
        today = datetime.datetime.strptime(today, "%Y-%m-%d").date()


    if request.method == "POST":
        present_ids = request.POST.getlist("present_workers")
        workers = Worker.objects.all()

        # Delete existing records for the selected date
        Attendance.objects.filter(date=today).delete()

        # Create new attendance records
        for worker in workers:
            if str(worker.id) in present_ids:
                Attendance.objects.create(worker=worker, date=today)

        return redirect('dashboard')  # ✅ redirect to dashboard after submission

    # On GET request, show form with pre-marked checkboxes if attendance exists
    workers = Worker.objects.all()
    present_worker_ids = Attendance.objects.filter(date=today).values_list('worker_id', flat=True)


    return render(request, 'worker/mark_attendance.html', {
        'workers': workers,
        'present_worker_ids': list(present_worker_ids),
        'today': today,
    })







def monthly_salary_view(request):
    # Default: current month and year
    year = int(request.GET.get('year', now().year))
    month = int(request.GET.get('month', now().month))

    # First and last day of month
    first_day = datetime.date(year, month, 1)
    if month == 12:
        last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    # Get all workers annotated with attendance count filtered by month
    from .models import Worker, Attendance

    workers = Worker.objects.all().annotate(
        days_worked=Count('attendance', filter=Q(attendance__date__range=(first_day, last_day)))
    )

    context = {
        'workers': workers,
        'year': year,
        'month': month,
        'month_name': first_day.strftime('%B'),
    }
    days = range(1, 32) 
    return render(request, 'worker/monthly_salary.html', context)




@login_required
def mark_paid_view(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)
    
    # Delete all attendance records of this worker
    Attendance.objects.filter(worker=worker).delete()

    return redirect('monthly_salary')

