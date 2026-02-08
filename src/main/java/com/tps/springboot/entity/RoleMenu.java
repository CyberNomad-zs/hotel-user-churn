package com.tps.springboot.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
@TableName("sys_role_menu")
@Data
public class RoleMenu {
    @TableId(type = IdType.AUTO) // 如果数据库是自增，加上 type = IdType.AUTO
    private Integer id;
    private Integer roleId;
    private Integer menuId;

}
