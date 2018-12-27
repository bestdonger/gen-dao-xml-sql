# 自动生成工具

根据实体类自动生成java mybatis相关的xml文件，dao文件，建表sql文件。

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

之后的就是字段名了，注释需以`//`开头，在字段上一行或者字段之后都可以
