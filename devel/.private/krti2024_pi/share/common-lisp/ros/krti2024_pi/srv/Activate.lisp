; Auto-generated. Do not edit!


(cl:in-package krti2024_pi-srv)


;//! \htmlinclude Activate-request.msg.html

(cl:defclass <Activate-request> (roslisp-msg-protocol:ros-message)
  ((data
    :reader data
    :initarg :data
    :type cl:boolean
    :initform cl:nil)
   (target
    :reader target
    :initarg :target
    :type cl:fixnum
    :initform 0))
)

(cl:defclass Activate-request (<Activate-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Activate-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Activate-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name krti2024_pi-srv:<Activate-request> is deprecated: use krti2024_pi-srv:Activate-request instead.")))

(cl:ensure-generic-function 'data-val :lambda-list '(m))
(cl:defmethod data-val ((m <Activate-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-srv:data-val is deprecated.  Use krti2024_pi-srv:data instead.")
  (data m))

(cl:ensure-generic-function 'target-val :lambda-list '(m))
(cl:defmethod target-val ((m <Activate-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-srv:target-val is deprecated.  Use krti2024_pi-srv:target instead.")
  (target m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Activate-request>) ostream)
  "Serializes a message object of type '<Activate-request>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'data) 1 0)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'target)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Activate-request>) istream)
  "Deserializes a message object of type '<Activate-request>"
    (cl:setf (cl:slot-value msg 'data) (cl:not (cl:zerop (cl:read-byte istream))))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'target)) (cl:read-byte istream))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Activate-request>)))
  "Returns string type for a service object of type '<Activate-request>"
  "krti2024_pi/ActivateRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Activate-request)))
  "Returns string type for a service object of type 'Activate-request"
  "krti2024_pi/ActivateRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Activate-request>)))
  "Returns md5sum for a message object of type '<Activate-request>"
  "62bff225506042c8c22b370ac260f09e")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Activate-request)))
  "Returns md5sum for a message object of type 'Activate-request"
  "62bff225506042c8c22b370ac260f09e")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Activate-request>)))
  "Returns full string definition for message of type '<Activate-request>"
  (cl:format cl:nil "# this .srv needed for ~%~%# activating target detection under '/vision/activate/target'~%~%bool data~%uint8 target~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Activate-request)))
  "Returns full string definition for message of type 'Activate-request"
  (cl:format cl:nil "# this .srv needed for ~%~%# activating target detection under '/vision/activate/target'~%~%bool data~%uint8 target~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Activate-request>))
  (cl:+ 0
     1
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Activate-request>))
  "Converts a ROS message object to a list"
  (cl:list 'Activate-request
    (cl:cons ':data (data msg))
    (cl:cons ':target (target msg))
))
;//! \htmlinclude Activate-response.msg.html

(cl:defclass <Activate-response> (roslisp-msg-protocol:ros-message)
  ((result
    :reader result
    :initarg :result
    :type cl:boolean
    :initform cl:nil))
)

(cl:defclass Activate-response (<Activate-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Activate-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Activate-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name krti2024_pi-srv:<Activate-response> is deprecated: use krti2024_pi-srv:Activate-response instead.")))

(cl:ensure-generic-function 'result-val :lambda-list '(m))
(cl:defmethod result-val ((m <Activate-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader krti2024_pi-srv:result-val is deprecated.  Use krti2024_pi-srv:result instead.")
  (result m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Activate-response>) ostream)
  "Serializes a message object of type '<Activate-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'result) 1 0)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Activate-response>) istream)
  "Deserializes a message object of type '<Activate-response>"
    (cl:setf (cl:slot-value msg 'result) (cl:not (cl:zerop (cl:read-byte istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Activate-response>)))
  "Returns string type for a service object of type '<Activate-response>"
  "krti2024_pi/ActivateResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Activate-response)))
  "Returns string type for a service object of type 'Activate-response"
  "krti2024_pi/ActivateResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Activate-response>)))
  "Returns md5sum for a message object of type '<Activate-response>"
  "62bff225506042c8c22b370ac260f09e")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Activate-response)))
  "Returns md5sum for a message object of type 'Activate-response"
  "62bff225506042c8c22b370ac260f09e")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Activate-response>)))
  "Returns full string definition for message of type '<Activate-response>"
  (cl:format cl:nil "bool result ~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Activate-response)))
  "Returns full string definition for message of type 'Activate-response"
  (cl:format cl:nil "bool result ~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Activate-response>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Activate-response>))
  "Converts a ROS message object to a list"
  (cl:list 'Activate-response
    (cl:cons ':result (result msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'Activate)))
  'Activate-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'Activate)))
  'Activate-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Activate)))
  "Returns string type for a service object of type '<Activate>"
  "krti2024_pi/Activate")