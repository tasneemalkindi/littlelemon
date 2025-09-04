from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import MenuFood, MenuCategory, Drinks, Reservation, Table, DrinksCategory, Review
from .forms import ContactForm, ReservationForm, LoginForm, RegisterForm, ReviewForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from datetime import datetime, time as dtime, timedelta
from django.utils.timezone import now as tz_now
from django.utils import timezone
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator



from .models import Reservation, Table
from .forms import ReservationForm

def home(request):
    categories = MenuCategory.objects.all().order_by('menu_category_name')

    if request.method == "POST" and request.POST.get("form_type") == "review":
        data = request.POST.copy()
        if request.user.is_authenticated:
            # inject name so form validation passes
            data["name"] = request.user.get_full_name() or request.user.username
        form = ReviewForm(data)
        if form.is_valid():
            review = form.save(commit=False)
            if request.user.is_authenticated:
                review.user = request.user
            review.is_approved = False
            review.save()
            return redirect("home")
    else:
        form = ReviewForm()

    approved = Review.objects.filter(is_approved=True).order_by("-created_at")
    stats = approved.aggregate(avg=Avg("rating"), total=Count("id"))

    paginator = Paginator(approved, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "review_form": form,
        "page_obj": page_obj,
        "avg_rating": stats["avg"] or 0,
        "total_reviews": stats["total"] or 0,
    }
    return render(request, "restaurant/home.html", context)


def menu(request):
    # read filters from query string 
    category_id = request.GET.get('category')  # food category
    q = request.GET.get('q', '').strip() #search query 
    max_price = request.GET.get('max_price')

    # base category lists
    categories_qs = MenuCategory.objects.all().order_by('menu_category_name')
    drink_categories_qs = DrinksCategory.objects.all().order_by('drink_category_name')

    # price filter
    price_filter = Q()
    if max_price:
        price_filter &= Q(price__lte=max_price)

    # text search filter
    search_filter = Q()
    if q:
        search_filter = Q(food_name__icontains=q) | Q(description__icontains=q)

    if category_id:
        categories_qs = categories_qs.filter(id=category_id)

    # foods grouped by category with filters applied
    foods_by_category = {
        category: category.category_name.filter(price_filter & search_filter).order_by('food_name')
        for category in categories_qs
    }

    # drinks grouped by drinks category
    drinks_search_filter = Q()
    if q:
        drinks_search_filter = Q(drink_name__icontains=q)

    drinks_by_category = {
        dcat: Drinks.objects.filter(categories=dcat).filter(price_filter & drinks_search_filter).order_by('drink_name')
        for dcat in drink_categories_qs
    }

    return render(request, 'restaurant/menu.html', {
        'categories_all': MenuCategory.objects.all().order_by('menu_category_name'),  # for dropdown
        'selected_category': category_id,
        'q': q,
        'max_price': max_price or '',
        'foods_by_category': foods_by_category,
        'drinks_by_category': drinks_by_category,
    })

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("thank_you")
    else:
        form = ContactForm()
    
    return render(request, 'restaurant/contact.html', {'form': form})

def thank_you(request):
    return render(request, 'restaurant/thank_you.html')

@staff_member_required
def staff_reservations_view(request):
    reservations = Reservation.objects.order_by('date', 'time')
    return render(request, 'restaurant/staff_reservations.html', {'reservations': reservations})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()

    return render (request, "restaurant/login.html", {"form":form}) 

@login_required 
def my_reservations(request):
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # Upcoming reservations
    upcoming_future = Reservation.objects.filter(user=request.user, date__gt=today)
    upcoming_today  = Reservation.objects.filter(user=request.user, date=today, time__gte=now_time)
    upcoming = (upcoming_future | upcoming_today).order_by('date', 'time')

    # Past reservations
    past_before = Reservation.objects.filter(user=request.user, date__lt=today)
    past_today  = Reservation.objects.filter(user=request.user, date=today, time__lt=now_time)
    past = (past_before | past_today).order_by('-date', '-time')

    return render(request, 'restaurant/my_reservations.html', {
        'reservations_upcoming': upcoming,
        'reservations_past': past,
    })

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirect to login page after registering
    else:
        form = RegisterForm()
    return render(request, 'restaurant/register.html', {'form': form})

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    reservation.delete() 
    return redirect('my_reservations') 








# Information about the slots 
SLOT_MINUTES = 45
OPEN_TIME = dtime(12, 0)   # 12:00 PM
CLOSE_TIME = dtime(23, 0)  # 11:00 PM

# Create 45 minutes slots from open to close 
def _generate_slots_for(date_obj):
    start_dt = datetime.combine(date_obj, OPEN_TIME)
    end_dt = datetime.combine(date_obj, CLOSE_TIME)
    slots = []
    while start_dt < end_dt:
        slots.append(start_dt.time())
        start_dt += timedelta(minutes=SLOT_MINUTES)
    return slots

#Hide past times/dates
def _slot_is_future(date_obj, t):
    current = localtime() 
    today = current.date()

    if date_obj < today:
        return False
    if date_obj > today:
        return True
    return t > current.time()


# Find a table that meets requirements
def find_table(date_obj, t, party_size, is_shared):

    if t not in _generate_slots_for(date_obj):
        return None
    if not _slot_is_future(date_obj, t):
        return None
    
    candidates = list(
        Table.objects
        .filter(capacity__gte=party_size, allows_shared=is_shared)
        .order_by('capacity')
    )
    if not candidates:
        return None

    candidate_ids = [tb.id for tb in candidates]

    # Private
    if not is_shared:
        occupied_ids = set(
            Reservation.objects
            .filter(date=date_obj, time=t, table_id__in=candidate_ids)
            .values_list('table_id', flat=True)
        )
        for tb in candidates:
            if tb.id not in occupied_ids:
                return tb
        return None

    # Shared 
    private_ids = set(
        Reservation.objects
        .filter(date=date_obj, time=t, is_shared=False, table_id__in=candidate_ids)
        .values_list('table_id', flat=True)
    )

    shared_used = {}
    for row in (
        Reservation.objects
        .filter(date=date_obj, time=t, is_shared=True, table_id__in=candidate_ids)
        .values('table_id', 'party_size')
    ):
        tid = row['table_id']
        shared_used[tid] = shared_used.get(tid, 0) + row['party_size']

    # Choose the smallest table with enough remaining seats
    for tb in candidates:
        if tb.id in private_ids:
            continue
        remaining = tb.capacity - shared_used.get(tb.id, 0)
        if remaining >= party_size:
            return tb

    return None


@login_required
def reservation_view(request):
    if request.method == "POST":
        form = ReservationForm(request.POST, user=request.user)
        if form.is_valid():
            date = form.cleaned_data['date']
            if Reservation.objects.filter(user=request.user, date=date).exists():
                form.add_error('date', "You can only reserve one table per day.")
            else:
                time_val = form.cleaned_data['time']
                party_size = form.cleaned_data['party_size']
                is_shared = form.cleaned_data['is_shared']

                chosen = find_table(date, time_val, party_size, is_shared)
                if chosen is None:
                    form.add_error('time', "This slot just got taken. Please pick another.")
                else:
                    reservation = form.save(commit=False)
                    reservation.user = request.user
                    reservation.table = chosen
                    reservation.save()
                    return render(request, 'restaurant/reservation_confirmed.html', {'reservation': reservation})
    else:
        form = ReservationForm(user=request.user)

    return render(request, 'restaurant/reservation.html', {'form': form})



@login_required
def available_slots(request):
    
    date_str = request.GET.get('date')
    party_size = request.GET.get('party_size')
    is_shared = request.GET.get('is_shared')


    from datetime import datetime
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return JsonResponse({'error': 'Invalid date'}, status=400)

    # Check if user already has a reservation for this date
    if Reservation.objects.filter(user=request.user, date=date_obj).exists():
        return JsonResponse({'error': 'You can only reserve one table per day.'})
    try:
        if not date_str or not party_size or is_shared is None:
            return JsonResponse({"available": [], "full": []})
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        party_size = int(party_size)
        is_shared = (str(is_shared).lower() == 'true')
    except Exception:
        return JsonResponse({"available": [], "full": []})

    # Build lists for available and full 
    available, full = [], []
    for t in _generate_slots_for(date_obj):

        if not _slot_is_future(date_obj, t):  
            continue

        if find_table(date_obj, t, party_size, is_shared):
            target = available
        else:
            target = full

        target.append({
            "value": t.strftime("%H:%M"),
            "label": t.strftime("%I:%M %p"),
        })

    return JsonResponse({"available": available, "full": full})

