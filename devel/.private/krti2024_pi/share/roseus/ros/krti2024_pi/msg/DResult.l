;; Auto-generated. Do not edit!


(when (boundp 'krti2024_pi::DResult)
  (if (not (find-package "KRTI2024_PI"))
    (make-package "KRTI2024_PI"))
  (shadow 'DResult (find-package "KRTI2024_PI")))
(unless (find-package "KRTI2024_PI::DRESULT")
  (make-package "KRTI2024_PI::DRESULT"))

(in-package "ROS")
;;//! \htmlinclude DResult.msg.html


(defclass krti2024_pi::DResult
  :super ros::object
  :slots (_is_found _dx _dy _dx_m _dy_m ))

(defmethod krti2024_pi::DResult
  (:init
   (&key
    ((:is_found __is_found) nil)
    ((:dx __dx) 0)
    ((:dy __dy) 0)
    ((:dx_m __dx_m) 0.0)
    ((:dy_m __dy_m) 0.0)
    )
   (send-super :init)
   (setq _is_found __is_found)
   (setq _dx (round __dx))
   (setq _dy (round __dy))
   (setq _dx_m (float __dx_m))
   (setq _dy_m (float __dy_m))
   self)
  (:is_found
   (&optional (__is_found :null))
   (if (not (eq __is_found :null)) (setq _is_found __is_found)) _is_found)
  (:dx
   (&optional __dx)
   (if __dx (setq _dx __dx)) _dx)
  (:dy
   (&optional __dy)
   (if __dy (setq _dy __dy)) _dy)
  (:dx_m
   (&optional __dx_m)
   (if __dx_m (setq _dx_m __dx_m)) _dx_m)
  (:dy_m
   (&optional __dy_m)
   (if __dy_m (setq _dy_m __dy_m)) _dy_m)
  (:serialization-length
   ()
   (+
    ;; bool _is_found
    1
    ;; int32 _dx
    4
    ;; int32 _dy
    4
    ;; float32 _dx_m
    4
    ;; float32 _dy_m
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _is_found
       (if _is_found (write-byte -1 s) (write-byte 0 s))
     ;; int32 _dx
       (write-long _dx s)
     ;; int32 _dy
       (write-long _dy s)
     ;; float32 _dx_m
       (sys::poke _dx_m (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _dy_m
       (sys::poke _dy_m (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _is_found
     (setq _is_found (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; int32 _dx
     (setq _dx (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _dy
     (setq _dy (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; float32 _dx_m
     (setq _dx_m (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _dy_m
     (setq _dy_m (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get krti2024_pi::DResult :md5sum-) "bdb57b108ed455ecab1cab6b0ba9017d")
(setf (get krti2024_pi::DResult :datatype-) "krti2024_pi/DResult")
(setf (get krti2024_pi::DResult :definition-)
      "bool is_found
int32 dx
int32 dy
float32 dx_m
float32 dy_m
")



(provide :krti2024_pi/DResult "bdb57b108ed455ecab1cab6b0ba9017d")


