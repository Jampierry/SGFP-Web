from django.core.management.base import BaseCommand
from core.models import Configuracao

NOVOS_TEMAS = [
    'corona-dark',
    'vanta-dark',
    'futureui-color',
    'material-light',
]

class Command(BaseCommand):
    help = 'Define o tema de todos os usuários para um dos temas válidos. Use --tema=<tema> para escolher.'

    def add_arguments(self, parser):
        parser.add_argument('--tema', type=str, help='Tema a ser aplicado para todos os usuários')

    def handle(self, *args, **options):
        tema = options.get('tema')
        if tema and tema not in NOVOS_TEMAS:
            self.stdout.write(self.style.ERROR(f'Tema inválido. Escolha um dos: {", ".join(NOVOS_TEMAS)}'))
            return
        if tema:
            alterados = 0
            for conf in Configuracao.objects.all():
                conf.dashboard_tema = tema
                conf.save()
                alterados += 1
            self.stdout.write(self.style.SUCCESS(f'Tema "{tema}" aplicado para {alterados} usuários.'))
        else:
            for tema in NOVOS_TEMAS:
                alterados = 0
                for conf in Configuracao.objects.all():
                    conf.dashboard_tema = tema
                    conf.save()
                    alterados += 1
                self.stdout.write(self.style.SUCCESS(f'Tema "{tema}" aplicado para {alterados} usuários.')) 