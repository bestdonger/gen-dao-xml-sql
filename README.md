# 自动生成工具

> 脚本比较简单，可自行更改以适应更多场景

根据实体类自动生成java mybatis相关的xml文件，dao文件，建表sql文件

将实体类写入文件，运行`python3 gen_dao_xml_sql.py 实体类文件的路径`

就会在实体类所在目录下生成对应的三个文件，可自行拷贝至项目中

支持的字段类型为
```
int, long, byte, short, float, double,
Integer, Long, Byte, Short, Float, Double,
Date, LocalDateTime, LocalDate // 这三种类型生成的sql字段类型统一为datetime
```

实体类格式
```
namespace:com.bestdonger.dao.UserDAO
entity:com.bestdonger.entity.User

private Long id;
// 姓名
private String name;

private Integer age; // 年龄
private Date birthday; // 生日

```

第一行为`namespace:`加上dao层接口的包名+类名

第二行为`entity:`加上实体类的包名+类名

之后的就是字段名了，注释需以`//`开头，在字段上一行或者字段之后都可以，会作为sql中的`comment`写入`.sql`文件
