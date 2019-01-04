from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserLoginForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, View
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .shared import is_member,is_in_multiple_groups

@method_decorator(never_cache, name='dispatch')
class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'common/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not is_in_multiple_groups(request.user,['wetlab','bioinformatics']):
                        return redirect('collaborator_app:collaboratorsetqcs')
                    else:
                        return redirect('nextseq_app:userruns')
            else:
                return render(request, self.template_name, {'form': form, 'error_message': 'Invalid login'})

        return render(request, self.template_name, {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, form.user)
            #messages.success(request, 'Your password was successfully updated!')

            return redirect('nextseq_app:userruns')
        # else:
            #messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'common/change_password.html', {
        'form': form
    })



class UserRegisterView(FormView):
    form_class = UserRegisterForm
    template_name = 'common/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return HttpResponseRedirect(self.success_url)















