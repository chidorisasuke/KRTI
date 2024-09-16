
(cl:in-package :asdf)

(defsystem "krti2024_pi-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Activate" :depends-on ("_package_Activate"))
    (:file "_package_Activate" :depends-on ("_package"))
  ))