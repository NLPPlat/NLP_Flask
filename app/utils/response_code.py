# coding:utf-8

class RET:
    OK                    = 200
    CREATED               = 201
    ACCEPTED              = 202
    NO_CONTENT            = 204
    UNAUTHORIZED          = 401
    FORBBIDEN             = 403
    NOT_FOUND             = 404
    NOT_ACCEPTABLE        = 406
    GONE                  = 410
    UNPROCESABLE_ENTITY   = 422
    INTERNAL_SERVER_ERROR = 500

error_map = {
    RET.OK                    : u"成功",
    RET.CREATED               : u"新建或修改数据成功"
}
