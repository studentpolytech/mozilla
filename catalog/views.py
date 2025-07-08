from django.shortcuts import render
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin  # Добавил PermissionRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# Новое представление для библиотекарей с проверкой разрешения
class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

# Class-based views first
class BookListView(generic.ListView):
    model = Book
    paginate_by = 1

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

# Then function-based views
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_with_word = Book.objects.filter(title__icontains='the').count()
    
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
        
    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,                       
            'num_books_with_word': num_books_with_word,
            'num_visits': num_visits,
        },
    )



from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


#______________________________________________________________ руководство 9
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

@login_required
def borrow_book(request, pk):
    """Позволяет пользователю взять книгу."""
    book_instance = get_object_or_404(BookInstance, pk=pk, status='a')  # Только доступные книги
    
    if request.method == 'POST':
        book_instance.status = 'o'  # 'o' = on loan
        book_instance.borrower = request.user
        book_instance.due_back = timezone.now() + timezone.timedelta(weeks=4)  # Срок возврата через 4 недели
        book_instance.save()
        return redirect('my-borrowed')  # Перенаправляем в "Мои книги"
    
    return redirect('book-detail', pk=book_instance.book.pk)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
#---------------------------------------  Примечание: Наблюдательные пользователи могли заметить, что мы ничего не делаем, чтобы предотвратить несанкционированный доступ к страницам! Мы оставили это в качестве упражнения для вас (подсказка: вы можете использовать PermissionRequiredMixin и, либо создать новое разрешение, или воспользоваться нашим прежним can_mark_returned).

from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

class AuthorCreate(PermissionRequiredMixin, generic.CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/author_form.html'

class AuthorUpdate(PermissionRequiredMixin, generic.UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/author_form.html'

class AuthorDelete(PermissionRequiredMixin, generic.DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/author_confirm_delete.html'
    success_url = reverse_lazy('authors')

#______________ проверьте себя руководство 9
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Book

class BookCreate(CreateView):
    model = Book
    fields = '__all__'  # или перечисли нужные поля
    success_url = '/catalog/books/'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    success_url = '/catalog/books/'

class BookDelete(DeleteView):
    model = Book
    success_url = '/catalog/books/'
