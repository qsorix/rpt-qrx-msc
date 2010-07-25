FILTER='--filter=eps-builtin'
EXT=eps

dia konfiguracja-model-lab-mapping.dia ${FILTER} --show-layers=model --export=konfiguracja-model.${EXT}
dia konfiguracja-model-lab-mapping.dia ${FILTER} --show-layers=laboratory --export=konfiguracja-laboratory.${EXT}
dia konfiguracja-model-lab-mapping.dia ${FILTER} --show-layers=model,laboratory,mapping --export=konfiguracja-mapping.${EXT}
