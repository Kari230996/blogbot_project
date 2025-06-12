from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ninja.responses import Response
from .models import Post
from .schemas import PostSchema, PostInSchema

router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            return User.objects.get(auth_token__key=token)
        except User.DoesNotExist:
            return None


auth = AuthBearer()


class LoginSchema(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    token: str


@router.post("/login", response=TokenSchema)
def login(request, data: LoginSchema):
    from django.contrib.auth import authenticate
    user = authenticate(username=data.username, password=data.password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return {"token": token.key}
    return Response({"detail": "Неверный логин или пароль"}, status=401)


@router.get("/posts", response=list[PostSchema])
def list_posts(request):
    return Post.objects.all()


@router.get("/posts/{post_id}", response=PostSchema)
def get_post(request, post_id: int):
    return get_object_or_404(Post, id=post_id)


@router.post("/posts", response=PostSchema, auth=auth)
def create_post(request, data: PostInSchema):
    return Post.objects.create(**data.dict(), owner=request.auth)


@router.put("/posts/{post_id}", response=PostSchema, auth=auth)
def update_post(request, post_id: int, data: PostInSchema):
    post = get_object_or_404(Post, id=post_id)
    if post.owner != request.auth:
        return Response({"detail": "⛔ Недостаточно прав"}, status=403)
    for attr, value in data.dict().items():
        setattr(post, attr, value)
    post.save()
    return post


@router.delete("/posts/{post_id}", auth=auth)
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    if post.owner != request.auth:
        return Response({"detail": "⛔ Недостаточно прав"}, status=403)
    post.delete()
    return {"success": True}
