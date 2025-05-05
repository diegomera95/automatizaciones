# ALIAS ÚTILES CONFIGURADOS

1. Abrir el editor de cron directamente con nano
alias editar-cron='EDITOR=nano crontab -e'

2. Ver tareas programadas con cron
alias ver-cron='crontab -l'

3. Ver el log del script meta_gastos_mes.py
alias ver-meta-log='tail -n 50 /home/diego/cron_logs/meta.log'

---

💡 Puedes agregar estos alias a tu archivo ~/.zshrc o ~/.bashrc ejecutando:
echo "alias nombre='comando'" >> ~/.zshrc
source ~/.zshrc