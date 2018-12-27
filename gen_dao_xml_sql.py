import os
import re
import sys


def camel_underline(s):
    return re.sub('([A-Z])', '_\\1', s).lstrip('_').lower()


xml_template = '''
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{namespace}">

    <sql id="all_columns">
        {all_columns}
    </sql>
    
    <select id="findById" resultType="{entity_path}">
        select
        <include refid="all_columns"/>
        from {table}
        where id = #{{id}}
    </select>
    
    <select id="findByIds" resultType="{entity_path}">
        select
        <include refid="all_columns"/>
        from {table}
        where id in
            <foreach collection="ids" item="item" separator="," open="(" close=")">
                #{{item}}
            </foreach>
    </select>
    
    <insert id="insert">
        insert into {table}
            <trim suffixOverrides="," prefix="(" suffix=")">
{insert_columns}
            </trim>
        value
            <trim suffixOverrides="," prefix="(" suffix=")">
{insert_values}
            </trim>
    </insert>
    
    <update id="update">
        update {table}
        <set>
{update_sentences}
        </set>
        where id = #{{entity.id}}
    </update>
    
    <delete id="delete">
        delete from {table}
        where id = #{{id}}
    </delete>
</mapper>
'''

dao_template = '''package {package};

import {entity_path};
import org.apache.ibatis.annotations.Param;

import java.util.List;


public interface {interface} {{

    {entity} findById(@Param("id") Long id);
    
    List<{entity}> findByIds(@Param("ids") List<Long> ids);

    Long insert(@Param("entity") {entity} entity);

    Long update(@Param("entity") {entity} entity);

    Long delete(@Param("id") Long id);

}}
'''

sql_template = '''
create table `{table}` (
{table_fields}
) ENGINE=InnoDB default CHARSET=utf8mb4 collate=utf8mb4_bin;
'''


def _insert_if_column(field):
    return f'\t\t\t\t<if test="entity.{field} != null">{camel_underline(field)},</if>'


def _insert_if_value(field):
    return f'\t\t\t\t<if test="entity.{field} != null">{field},</if>'


def _update_if_sentence(field):
    return f'\t\t\t<if test="entity.{field} != null">{camel_underline(field)} = #{{{field}}},</if>'


def _sql_field(field_type_comment_item):
    field = field_type_comment_item[0]
    type_comment = field_type_comment_item[1]

    column = camel_underline(field)
    field_comment = type_comment[1]
    if type_comment[0] == 'String':
        column_type = 'varchar(255)'
        column_default = '\'\''
    elif type_comment[0] == 'Integer' or type_comment[0] == 'int':
        column_type = 'int'
        column_default = 0
    elif type_comment[0] == 'Long' or type_comment[0] == 'long':
        column_type = 'bigint'
        column_default = 0
    elif type_comment[0] == 'Boolean' or type_comment[0] == 'boolean':
        column_type = 'tinyint(1)'
        column_default = 0
    elif type_comment[0] == 'Byte' or type_comment[0] == 'byte':
        column_type = 'tinyint'
        column_default = 0
    elif type_comment[0] == 'Short' or type_comment[0] == 'short':
        column_type = 'smallint'
        column_default = 0
    elif type_comment[0] == 'Date' or type_comment[0] == 'LocalDateTime' or type_comment[0] == 'LocalDate':
        column_type = 'datetime(3)'
        column_default = 'now(3)'
    elif type_comment[0] == 'Double' or type_comment[0] == 'double' \
            or type_comment[0] == 'Float' or type_comment[0] == 'float':
        column_type = 'double'
        column_default = 0
    else:
        print(f'no column type matched {type_comment[0]}, varchar is the default')
        column_type = 'varchar(255)'
        column_default = '\'\''

    if column == 'id':
        return f'\t`{column}` {column_type} auto_increment primary key comment \'{field_comment}\''
    return f'\t`{column}` {column_type} not null default {column_default} comment \'{field_comment}\''


if __name__ == "__main__":
    ori_path = sys.argv[1]
    with open(ori_path, 'r') as ori_file:
        # 第一行
        namespace = ori_file.readline().split(':')[1].strip()
        package = '.'.join(namespace.split('.')[0:-1])
        interface = namespace.split('.')[-1]
        xml_path = os.path.join(os.path.dirname(os.path.abspath(ori_path)), namespace.split('.')[-1] + '.xml')
        dao_path = os.path.join(os.path.dirname(os.path.abspath(ori_path)), namespace.split('.')[-1] + '.java')

        # 第二行
        entity_path = ori_file.readline().split(':')[1].strip()
        entity = entity_path.split('.')[-1]
        table = camel_underline(entity_path.split('.')[-1])

        sql_path = os.path.join(os.path.dirname(os.path.abspath(ori_path)), camel_underline(entity) + '.sql')

        # 字段行
        field_type_comment = {}
        field_comment = ''
        for line in ori_file:
            if not line.strip():
                continue
            if line.strip().startswith('//'):
                field_comment = line.split('//')[1].strip()
                continue

            tmp_comment = line.split(';')[1].strip().lstrip('//').strip()
            field_comment = tmp_comment or field_comment
            tmp = line.split(';')[0].split()
            field_type_comment[tmp[-1]] = (tmp[-2], field_comment)
            field_comment = ''

        # 所有字段
        all_columns = ',\n\t\t'.join(map(camel_underline, field_type_comment.keys()))

        # insert相关
        insert_columns = '\n'.join(map(_insert_if_column, field_type_comment.keys()))
        insert_values = '\n'.join(map(_insert_if_value, field_type_comment.keys()))

        # update语句
        update_sentences = '\n'.join(map(_update_if_sentence, field_type_comment.keys()))

        # sql字段
        table_fields = ',\n'.join(map(_sql_field, field_type_comment.items()))

        # 写xml文件
        with open(xml_path, 'w') as xml_file:
            xml_file.write(
                xml_template.format(namespace=namespace, table=table, all_columns=all_columns, entity_path=entity_path,
                                    insert_columns=insert_columns, insert_values=insert_values,
                                    update_sentences=update_sentences))

        # 写dao java文件
        with open(dao_path, 'w') as dao_file:
            dao_file.write(
                dao_template.format(namespace=namespace, interface=interface, entity_path=entity_path, entity=entity,
                                    package=package))

        # 写sql文件
        with open(sql_path, 'w') as sql_file:
            sql_file.write(sql_template.format(table=table, table_fields=table_fields))

