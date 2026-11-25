#!/bin/bash
# Executado pelo systemd, como usuário dicbio: prepara uma versão completa do site
# (código, banco e HTML) numa pasta nova e só a põe no ar se tudo der certo.
set -euo pipefail
BASE=/srv/dicbio/site
RAMO=$(cat "$BASE/ramo.txt")
cd "$BASE/repo"
git fetch --quiet --depth 1 origin "$RAMO"
NOVO=$(git rev-parse FETCH_HEAD)
if [ "$NOVO" = "$(cat "$BASE/publicado.txt")" ]; then
  exit 0
fi

mkdir -p "$BASE/versoes"
VERSAO="$BASE/versoes/$(date +%Y%m%d-%H%M%S)-${NOVO:0:7}"
trap 'rm -rf "$VERSAO"' ERR
mkdir "$VERSAO"
git archive "$NOVO" | tar -x -C "$VERSAO"
cd "$VERSAO"
PY="$BASE/venv/bin/python"
export PYTHONUTF8=1
"$PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt

rm -f corpus_digital/obras_html/*.html
prepara() {
  "$PY" manage.py migrate &&
  "$PY" manage.py extract_corpus_terms --force-regen &&
  "$PY" manage.py import_obra_metadata &&
  "$PY" manage.py import_dictionary_data &&
  "$PY" manage.py processar_obras_tei --force &&
  "$PY" manage.py collectstatic --noinput
}
prepara > preparacao.log 2>&1 || { tail -n 20 preparacao.log; false; }

# Conferência antes de pôr no ar.
"$PY" manage.py shell -v 0 -c '
from django.conf import settings
from django.test import Client
from corpus_digital.models import Obra
from verbetes.models import OcorrenciaCorpus, Verbete
xml = len(list(settings.CORPUS_XML_ROOT.glob("*.xml")))
assert Obra.objects.count() == xml, "faltam obras no banco"
assert OcorrenciaCorpus.objects.exists(), "não há ocorrências"
enderecos = ["/", "/consulta/", "/documentacao/", "/corpus/"]
enderecos += [f"/corpus/{o.slug}/" for o in Obra.objects.all()]
enderecos += [f"/consulta/{v.slug}/" for v in Verbete.objects.all()[:5]]
c = Client(headers={"host": settings.ALLOWED_HOSTS[0]})
for e in enderecos:
    r = c.get(e, secure=True)
    assert r.status_code == 200, f"{e}: {r.status_code}"
for o in Obra.objects.all():
    assert (settings.BASE_DIR / "corpus_digital/obras_html" / f"{o.slug}.html").exists(), o.slug
'

ln -sfn "$VERSAO" "$BASE/atual.novo"
mv -T "$BASE/atual.novo" "$BASE/atual"
trap - ERR
echo "$NOVO" > "$BASE/publicado.txt"
touch "$BASE/reiniciar"   # o systemd, como root, reinicia o serviço

# Guarda as 3 últimas versões, para poder voltar atrás.
ls -1d "$BASE"/versoes/* | head -n -3 | xargs -r rm -rf
echo "Publicado: $NOVO"
