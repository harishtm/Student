from django.contrib.auth.models import User
from rest_framework import serializers
from info.models import *

class StudentSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True,error_messages={'required':'Please enter name'})
    age = serializers.CharField(required=True,error_messages={'required':'Please enter age'})

    class Meta:
        model = Student
        fields = ('name','age','address','phone')

#    def validate_name(self, value):
#        if (self.Meta.model).objects.filter(name__iexact=value).exists():
#            raise serializers.ValidationError('Name already exists in our database')
#        return value

    def validate(self, attrs):
        if self.instance:
            if (self.Meta.model).objects.exclude(id=self.instance.id).filter(name__iexact=attrs['name']).exists():
                raise serializers.ValidationError('Name already exists in our database')
        else:
            if (self.Meta.model).objects.filter(name__iexact=attrs['name']).exists():
                raise serializers.ValidationError('Name already exists in our database')
        if int(attrs['age']) <= 3 or int(attrs['age']) > 25:
            raise serializers.ValidationError('Age can not be less than 3 or greater than 25')
        return attrs


class StudentListSerializers(serializers.ListSerializer):

    child = StudentSerializer()
    allow_null = True
    many = True


"""
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('password', 'first_name', 'last_name', 'email',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = super(UserSerializer, self).restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user
"""


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data.get('username',''),
            email=validated_data.get('email',''),
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name',''),
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User


class UserAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = User







