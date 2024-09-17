
(cl:in-package :asdf)

(defsystem "krti2024_pi-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "DResult" :depends-on ("_package_DResult"))
    (:file "_package_DResult" :depends-on ("_package"))
  ))