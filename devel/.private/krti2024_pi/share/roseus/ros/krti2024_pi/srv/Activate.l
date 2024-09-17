;; Auto-generated. Do not edit!


(when (boundp 'krti2024_pi::Activate)
  (if (not (find-package "KRTI2024_PI"))
    (make-package "KRTI2024_PI"))
  (shadow 'Activate (find-package "KRTI2024_PI")))
(unless (find-package "KRTI2024_PI::ACTIVATE")
  (make-package "KRTI2024_PI::ACTIVATE"))
(unless (find-package "KRTI2024_PI::ACTIVATEREQUEST")
  (make-package "KRTI2024_PI::ACTIVATEREQUEST"))
(unless (find-package "KRTI2024_PI::ACTIVATERESPONSE")
  (make-package "KRTI2024_PI::ACTIVATERESPONSE"))

(in-package "ROS")





(defclass krti2024_pi::ActivateRequest
  :super ros::object
  :slots (_data _target ))

(defmethod krti2024_pi::ActivateRequest
  (:init
   (&key
    ((:data __data) nil)
    ((:target __target) 0)
    )
   (send-super :init)
   (setq _data __data)
   (setq _target (round __target))
   self)
  (:data
   (&optional (__data :null))
   (if (not (eq __data :null)) (setq _data __data)) _data)
  (:target
   (&optional __target)
   (if __target (setq _target __target)) _target)
  (:serialization-length
   ()
   (+
    ;; bool _data
    1
    ;; uint8 _target
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _data
       (if _data (write-byte -1 s) (write-byte 0 s))
     ;; uint8 _target
       (write-byte _target s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _data
     (setq _data (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; uint8 _target
     (setq _target (sys::peek buf ptr- :char)) (incf ptr- 1)
   ;;
   self)
  )

(defclass krti2024_pi::ActivateResponse
  :super ros::object
  :slots (_result ))

(defmethod krti2024_pi::ActivateResponse
  (:init
   (&key
    ((:result __result) nil)
    )
   (send-super :init)
   (setq _result __result)
   self)
  (:result
   (&optional (__result :null))
   (if (not (eq __result :null)) (setq _result __result)) _result)
  (:serialization-length
   ()
   (+
    ;; bool _result
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _result
       (if _result (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _result
     (setq _result (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(defclass krti2024_pi::Activate
  :super ros::object
  :slots ())

(setf (get krti2024_pi::Activate :md5sum-) "62bff225506042c8c22b370ac260f09e")
(setf (get krti2024_pi::Activate :datatype-) "krti2024_pi/Activate")
(setf (get krti2024_pi::Activate :request) krti2024_pi::ActivateRequest)
(setf (get krti2024_pi::Activate :response) krti2024_pi::ActivateResponse)

(defmethod krti2024_pi::ActivateRequest
  (:response () (instance krti2024_pi::ActivateResponse :init)))

(setf (get krti2024_pi::ActivateRequest :md5sum-) "62bff225506042c8c22b370ac260f09e")
(setf (get krti2024_pi::ActivateRequest :datatype-) "krti2024_pi/ActivateRequest")
(setf (get krti2024_pi::ActivateRequest :definition-)
      "# this .srv needed for 

# activating target detection under '/vision/activate/target'

bool data
uint8 target
---
bool result 
")

(setf (get krti2024_pi::ActivateResponse :md5sum-) "62bff225506042c8c22b370ac260f09e")
(setf (get krti2024_pi::ActivateResponse :datatype-) "krti2024_pi/ActivateResponse")
(setf (get krti2024_pi::ActivateResponse :definition-)
      "# this .srv needed for 

# activating target detection under '/vision/activate/target'

bool data
uint8 target
---
bool result 
")



(provide :krti2024_pi/Activate "62bff225506042c8c22b370ac260f09e")


