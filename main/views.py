from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q
import calendar
import datetime
from main.models import Employee, Attendance
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def home(request):
    return render(request, 'main/index.html')


@login_required
def attendance(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            date = request.POST.get('date')
            for employee, status in request.POST.items():
                print(employee)
                print(f"status {status}")
                if employee.startswith('status-'):
                    employee_id = employee[7:]
                    employee = Employee.objects.get(slug=employee_id)
                    attendance = Attendance.objects.create(employee=employee, date=date, status=status)
                    attendance.save()
            return redirect('main:home')
        else:
            employees = Employee.objects.all()
            context = {'employees': employees}
            return render(request, 'main/attendance_table.html', context)
    else:
        return redirect('main:home')


@login_required
def get_attendance_report(request):
    employees = Employee.objects.all()
    context = {'employees': employees}
    if request.user.is_superuser:
        if request.method == 'POST':
            start = request.POST.get('start')
            end = request.POST.get('end')
            if request.POST.get('username'):
                username = request.POST.get('username')
                if username == 'All Employees':
                    attendance_list = Attendance.objects.filter(date__range=(start, end))
                    context = {'attendance_list': attendance_list, 'employees': employees}
                    return render(request, 'main/attendance_report.html', context)
                else:
                    employee = Employee.objects.get(slug=username)
                    attendance_list = Attendance.objects.filter(employee=employee, date__range=(start, end))
                    context = {'attendance_list': attendance_list, 'employees': employees}
                    return render(request, 'main/attendance_report.html', context)
    return render(request, 'main/attendance_report.html', context)


@login_required
def get_employee_attendance(request):
    employees = Employee.objects.all()
    context = {'employees': employees}
    if request.user.is_superuser:
        if request.method == 'POST':
            start = request.POST.get('start')
            end = request.POST.get('end')
            if request.POST.get('username'):
                username = request.POST.get('username')
                if username == 'All Employees':
                    attendance_list = Attendance.objects.filter(date__range=(start, end)).values('employee__employee__first_name').annotate(present=Count('status', filter=Q(status='Present')), absent=Count('status', filter=Q(status='Absent')))
                    context = {'attendance_list': attendance_list, 'start': start, 'end': end, 'employees': employees}
                    return render(request, 'main/attendance_combined.html', context)
                else:
                    employee = Employee.objects.get(slug=username)
                    attendance_list = Attendance.objects.filter(employee=employee, date__range=(start, end)).values('employee__employee__first_name').annotate(present=Count('status', filter=Q(status='Present')), absent=Count('status', filter=Q(status='Absent')))
                    context = {'attendance_list': attendance_list, 'start': start, 'end': end, 'employees': employees}
                    return render(request, 'main/attendance_combined.html', context)
    return render(request, 'main/attendance_combined.html', context)