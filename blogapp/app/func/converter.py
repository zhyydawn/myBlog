from werkzeug.routing import BaseConverter


#自定义转换器
class RegexConverter(BaseConverter):
    def __init__(self, map, regex):
        super().__init__(map)
        self.regex = regex

    # 接受转换器里面的值 返回给试图函数
    def to_python(self, value):
        return super().to_python(value)
    #接受视图函数里面需要处理的跳转的视图函数的名字（url_for里面的视图），处理后解析为路由，返回为route
    def to_url(self, value):
        return super().to_url(value)


app.url_map.converters['re'] = RegexConverter
