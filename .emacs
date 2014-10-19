(add-to-list 'exec-path "/usr/local/bin")
(setq ispell-program-name "aspell")

;; Visual line mode

(add-hook 'text-mode-hook 'turn-on-visual-line-mode)

;; Font size
(set-face-attribute 'default nil :height 150)

;; Remove splash screen
(setq inhibit-splash-screen t)

;; Delete selection mode
(delete-selection-mode 1)

;; Loading PHP mode

(autoload 'php-mode "php-mode" "Major mode for editing php code." t)
(add-to-list 'auto-mode-alist '("\\.php$" . php-mode))
(add-to-list 'auto-mode-alist '("\\.inc$" . php-mode))
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

;; PDF mode for Latex

 (setq TeX-PDF-mode t)

;; spell checker

(setq ispell-program-name "aspell")

(setq ispell-program-name "aspell"
      ispell-dictionary "english"
      ispell-dictionary-alist
      (let ((default '("[A-Za-z]" "[^A-Za-z]" "[']" nil
                       ("-B" "-d" "english" "--dict-dir"
                        "/Library/Application Support/cocoAspell/aspell6-en-6.0-0")
                       nil iso-8859-1)))
        `((nil ,@default)
          ("english" ,@default))))


;; spell check on the fly

 (dolist (hook '(text-mode-hook))
      (add-hook hook (lambda () (flyspell-mode 1))))
    (dolist (hook '(change-log-mode-hook log-edit-mode-hook))
      (add-hook hook (lambda () (flyspell-mode -1))))


;; Disable backup

(setq auto-save-default nil)

;; Auctex master file

;;(setq-default TeX-master "paper") ; Query for master file.
