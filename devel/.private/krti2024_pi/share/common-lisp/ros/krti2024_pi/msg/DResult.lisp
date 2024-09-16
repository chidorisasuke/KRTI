; Auto-generated. Do not edit!


(cl:in-package krti2024_pi-msg)


;//! \htmlinclude DResult.msg.html

(cl:defclass <DResult> (roslisp-msg-protocol:ros-message)
  ((is_found
    :reader is_found
    :initarg :is_found
    :type cl:boolean
    :initform cl:nil)
   (dx
    :reader dx
    :initarg :dx
    :type cl:integer
    :initform 0)
   (dy
    :reader dy
    :initarg :dy
    :type cl:integer
    :initform 0)
   (dx_m
    :reader dx_m
    :initarg :dx_m
    :type cl:float
    :initform 0.0)
   (dy_m
    :reader dy_m
    :initarg :dy_m
    :type cl:float
    :initform 0.0))
)

(cl:defclass DResult (<DResult>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <DResult>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'DResult)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name krti2024_pi-msg:<DResult> is deprecated: use krti2024_pi-msg:DResult instead.")))

(cl:ensure-generic-function 'is_found-val :lambda-list '(m))
(cl:defmethod is_found-val ((m <DResult>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-msg:is_found-val is deprecated.  Use krti2024_pi-msg:is_found instead.")
  (is_found m))

(cl:ensure-generic-function 'dx-val :lambda-list '(m))
(cl:defmethod dx-val ((m <DResult>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-msg:dx-val is deprecated.  Use krti2024_pi-msg:dx instead.")
  (dx m))

(cl:ensure-generic-function 'dy-val :lambda-list '(m))
(cl:defmethod dy-val ((m <DResult>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-msg:dy-val is deprecated.  Use krti2024_pi-msg:dy instead.")
  (dy m))

(cl:ensure-generic-function 'dx_m-val :lambda-list '(m))
(cl:defmethod dx_m-val ((m <DResult>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-msg:dx_m-val is deprecated.  Use krti2024_pi-msg:dx_m instead.")
  (dx_m m))

(cl:ensure-generic-function 'dy_m-val :lambda-list '(m))
(cl:defmethod dy_m-val ((m <DResult>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-msg:dy_m-val is deprecated.  Use krti2024_pi-msg:dy_m instead.")
  (dy_m m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <DResult>) ostream)
  "Serializes a message object of type '<DResult>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'is_found) 1 0)) ostream)
  (cl:let* ((signed (cl:slot-value msg 'dx)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'dy)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'dx_m))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'dy_m))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <DResult>) istream)
  "Deserializes a message object of type '<DResult>"
    (cl:setf (cl:slot-value msg 'is_found) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'dx) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'dy) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'dx_m) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'dy_m) (roslisp-utils:decode-single-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<DResult>)))
  "Returns string type for a message object of type '<DResult>"
  "krti2024_pi/DResult")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'DResult)))
  "Returns string type for a message object of type 'DResult"
  "krti2024_pi/DResult")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<DResult>)))
  "Returns md5sum for a message object of type '<DResult>"
  "bdb57b108ed455ecab1cab6b0ba9017d")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'DResult)))
  "Returns md5sum for a message object of type 'DResult"
  "bdb57b108ed455ecab1cab6b0ba9017d")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<DResult>)))
  "Returns full string definition for message of type '<DResult>"
  (cl:format cl:nil "bool is_found~%int32 dx~%int32 dy~%float32 dx_m~%float32 dy_m~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'DResult)))
  "Returns full string definition for message of type 'DResult"
  (cl:format cl:nil "bool is_found~%int32 dx~%int32 dy~%float32 dx_m~%float32 dy_m~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <DResult>))
  (cl:+ 0
     1
     4
     4
     4
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <DResult>))
  "Converts a ROS message object to a list"
  (cl:list 'DResult
    (cl:cons ':is_found (is_found msg))
    (cl:cons ':dx (dx msg))
    (cl:cons ':dy (dy msg))
    (cl:cons ':dx_m (dx_m msg))
    (cl:cons ':dy_m (dy_m msg))
))
