from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from ninja.responses import codes_4xx
from pydantic import EmailStr, Field
import requests
from account.authorization import PasswordResetTokenAuthentication
from account.models import Otp
from account.schemas import AccountCreateBody, AccountOut, AccountLoginBody, PasswordResetToken, PasswordSchema, OtpIn
from account.authorization import TokenAuthentication, get_tokens_for_user
from django.contrib.auth import get_user_model, authenticate
from ninja import Router, File
from ninja.files import UploadedFile
from products.schemas.general import MessageOut
from django.core.mail import EmailMessage
from django.conf import settings

User = get_user_model()

account_router = Router(tags=['Accounts'])


@account_router.post('/signup', response={201: MessageOut, 400: MessageOut})
def register_user(request, payload: AccountCreateBody, image: UploadedFile = File(None)):
    if payload.password1 != payload.password2:
        return 400, {'msg': 'Passwords didn\'t match'}
    try:
        user = User.objects.get(email__iexact=payload.email)
        return 400, {'msg': 'Email is already used'}
    except User.DoesNotExist:
        user = User.objects.create_user(
            name=payload.name, email=payload.email, password=payload.password1
        )
        if image:
            res = requests.post(
                url=settings.IMGBB_URL,
                files={'image': image.read()},
                params={'key': settings.IMGBB_KEY}
            )
            if res.ok:
                data = res.json()['data']
                image_url = data['url']
                user.profile = image_url
                user.save()
        otp = Otp.objects.create(user=user)
        email_to_send = EmailMessage(
            subject='Your OTP code',
            body=f'This is your OTP code attached\n {otp.number}',
            from_email=settings.EMAIL_HOST_USER,
            to=[payload.email],
        )
        email_to_send.send(fail_silently=True)
        return 201, {'msg': "User created successfully"}


@account_router.post('/verify', response={200: MessageOut, codes_4xx: MessageOut})
def verify_user(request, email: EmailStr, otp: int):
    try:
        user = User.objects.get(email=email)
        user_otp = Otp.objects.get(user=user)
        if otp == user_otp.number:
            user_otp.delete()
            user.is_verified = True
            user.save()
            return 200, {'msg': 'User verified sucessfully'}
        else:
            return 404, {'msg': 'Otp was no match'}
    except User.DoesNotExist:
        return 404, {'msg': 'User was not found with that email'}


@account_router.post('/login', response={200: AccountOut, codes_4xx: MessageOut})
def login_user(request, paylod: AccountLoginBody):
    user = authenticate(email=paylod.email, password=paylod.password)
    if not user:
        return 404, {'msg': 'Email or password are incorrect, please try again'}
    if not user.is_verified:
        try:
            user_otp = Otp.objects.get(user=user)
            return 403, {'msg': 'Please Verify your account'}
        except Otp.DoesNotExist:
            otp = Otp.objects.create(user=user)
            mail_to_send = EmailMessage(
                subject='Password Reset',
                body=f"Your password reset otp is: {otp.number}",
                to=[user.email, ]
            )
            mail_to_send.send(fail_silently=True)
            return 403, {'msg': 'Please Verify your account'}
    token = get_tokens_for_user(user)
    print(token)
    return 200, {
        'token': token,
        'user': user
    }

@account_router.get('/me', auth=TokenAuthentication())
def get_user_info(request):
    user = get_object_or_404(User, id=request.auth['id'])
    return model_to_dict(user)
