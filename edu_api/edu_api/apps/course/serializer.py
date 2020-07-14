from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher


class CourseCategorySerializer(ModelSerializer):
    """课程分类"""

    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class CourseTeacherSerializer(ModelSerializer):
    """课程所属老师的序列化器"""

    class Meta:
        model = Teacher
        fields = ("id", "name", "title", "signature")


class CourseModelSerializer(ModelSerializer):
    """课程列表"""

    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher", "lesson_list"]
