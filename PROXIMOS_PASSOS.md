# Próximos passos — AstraMax Reviewer

Este roteiro conduz a versão `0.1.0` da implementação local validada até a
instalação real e a publicação. As etapas abaixo descrevem trabalho futuro;
a existência deste arquivo não significa que elas foram executadas.

## Situação de partida

- A implementação foi enviada para `main` em `alencardoug/astramax`, no commit
  `edeb0c1`.
- A validação local e os 25 testes de regressão passaram.
- O pacote npm foi gerado e seus dez arquivos foram conferidos contra a origem.
- O coletor extraído do pacote funcionou fora do repositório alvo.
- Ainda faltam validação oficial, instalação pelos gerenciadores, confirmação
  do ambiente Astra, revisão real e publicação no npm.

O envio de código ao GitHub não comprova visibilidade pública, descoberta em
índices ou instalação pelo SkillPM. Consulte as evidências locais em
[docs/VALIDATION.md](docs/VALIDATION.md).

## Como usar este roteiro

Execute as etapas em ordem. Registre resultados observados, incluindo falhas e
limitações, antes de marcar uma etapa como concluída. Se houver correções,
repita as verificações afetadas sobre a versão corrigida.

Os exemplos de `npx skills-ref`, `npx skills` e `npx skillpm` vêm da especificação
e da documentação deste repositório. **Sua distribuição, versão e sintaxe ainda
precisam ser confirmadas.** Antes de executá-los, confirme a ferramenta e seu
mantenedor na fonte oficial correspondente. Quando possível, use a versão
confirmada explicitamente e registre o comando exato utilizado.

A criação deste roteiro usa somente informações do repositório. A execução das
etapas de integração exigirá acesso às ferramentas e serviços externos indicados.
Os comandos de publicação aparecem separados dos comandos de validação.

## 0. Identificar a versão que será validada

**Objetivo:** vincular os resultados a uma versão concreta do código.

Na raiz do repositório:

```bash
git status --short --branch
git rev-parse HEAD
node --version
npm --version
python3 --version
git --version
```

1. Anote o commit completo e eventuais alterações locais. A instalação pelo
   GitHub só poderá trazer alterações que já estiverem no remoto.
2. Confira `name`, `version` e os endereços em
   [package.json](package.json). O nome proposto é `astramax-reviewer` e a versão
   inicial é `0.1.0`.
3. Use o registro de validação local existente como ponto de partida. Se o código
   ou o ambiente mudou desde aquele registro, execute as verificações pertinentes:

   ```bash
   npm run validate
   npm test
   git diff --check
   ```

4. Guarde o caminho da origem para as comparações posteriores. Em uma sessão Bash
   iniciada na raiz deste repositório:

   ```bash
   ASTRAMAX_FONTE="$PWD"
   ```

Essa variável só guarda um caminho na sessão do terminal; não configura a skill.
Se abrir outro terminal, defina novamente o caminho correto.

**Concluído quando:** commit, estado local e versões utilizadas estiverem
registrados, sem falhas locais pendentes de avaliação.

## 1. Executar o validador oficial de Agent Skills

**Objetivo:** verificar o formato com a ferramenta oficial, além das regras
locais que já passaram.

1. Confirme a distribuição oficial do validador, a versão escolhida, seus
   requisitos e a forma de invocação. Não conclua que um pacote é o oficial
   apenas porque seu nome coincide com o exemplo.
2. Execute a forma confirmada contra a pasta canônica. O comando candidato
   previsto na especificação é:

   ```bash
   npx skills-ref validate skills/astramax-reviewer
   ```

3. Registre versão, comando exato, código de saída e saída relevante, com um
   caminho para o log completo quando necessário.
4. Se houver problemas, ajuste o frontmatter, a estrutura ou as referências
   apontadas. Preserve uma única fonte em
   [skills/astramax-reviewer/SKILL.md](skills/astramax-reviewer/SKILL.md).
5. Após a correção, execute novamente o validador oficial e `npm run validate`.
   Se a correção alterar comportamento do coletor, execute também `npm test`.

Se o comando proposto não existir ou não for a distribuição correta, registre
essa incompatibilidade e atualize os exemplos do repositório com a forma
efetivamente confirmada. Uma falha ao baixar ou iniciar a ferramenta não é um
resultado de validação da skill.

**Concluído quando:** o validador oficial aceitar a pasta canônica e houver
evidência reproduzível do resultado. `npm run validate` sozinho não encerra esta
etapa.

## 2. Testar a instalação pelo GitHub em um projeto limpo

**Objetivo:** comprovar que um usuário consegue obter a skill completa a partir
do repositório remoto.

1. Confirme que `https://github.com/alencardoug/astramax` pode ser acessado por
   quem não tem suas permissões privadas e contém o commit que será testado.
2. Se a etapa anterior produziu correções locais, revise, faça commit e envie
   essas correções antes de testar a instalação remota.
3. Crie um repositório descartável separado da origem. No mesmo terminal em
   que definiu `ASTRAMAX_FONTE`, em um ambiente com Bash e `mktemp`:

   ```bash
   ASTRAMAX_TESTE="$(mktemp -d)"
   git -C "$ASTRAMAX_TESTE" init
   cd "$ASTRAMAX_TESTE"
   ```

4. Confirme versão e sintaxe do instalador `skills`. Execute a forma confirmada
   do comando previsto no projeto:

   ```bash
   npx skills add https://github.com/alencardoug/astramax --skill astramax-reviewer
   ```

5. Se houver seleção de destino, escolha a instalação no projeto descartável e
   no host que será testado. Registre a pasta efetiva; não presuma que todos os
   hosts usam o mesmo diretório.
6. Confira se a instalação contém estes arquivos dentro de `astramax-reviewer`:

   ```text
   SKILL.md
   references/review-methodology.md
   references/finding-severity.md
   references/compatibility.md
   references/handoff.md
   scripts/dossier.py
   ```

7. Compare os arquivos instalados com a versão correspondente na origem. Se a
   origem local tiver alterações posteriores ao commit instalado, use a versão
   daquele commit na comparação.
8. Abra o projeto descartável no host escolhido. Confirme que a skill aparece
   com o nome `astramax-reviewer`, a descrição esperada e referências acessíveis.
   No fluxo com Claude Code e Codex, confira o acesso à skill em cada host pelo
   mecanismo que ele suporta. A instalação no autor não comprova que o revisor
   também a descobriu; registre como cada contexto carregou as instruções.
9. Confira `git status --short`. A instalação pode criar seus próprios arquivos
   de skill/configuração; registre quais. Não deve executar testes do projeto
   ou criar uma revisão automaticamente.

**Concluído quando:** a instalação remota funcionar, os seis arquivos estiverem
presentes e coerentes com a origem, e o host reconhecer a skill. Copiar a pasta
manualmente é um diagnóstico útil, mas não substitui este teste do instalador.

## 3. Testar uma revisão real com contextos independentes

**Objetivo:** verificar o comportamento completo, desde a preparação da entrega
até um relatório sustentado por evidências.

### 3.1. Confirmar o ambiente do revisor

1. Abra um contexto do Codex separado daquele que implementará a entrega.
2. Pela interface e pelos recursos de inspeção efetivamente disponíveis,
   confirme a versão do Codex, o modelo selecionado e o esforço de raciocínio.
3. Confirme que o modelo é GPT-6 Astra e que o esforço corresponde ao máximo
   suportado para ele naquele ambiente. Não deduza isso apenas de um rótulo
   como `high`, `xhigh` ou `max`.
4. Registre a fonte de confirmação. Não copie credenciais ou arquivos de
   autenticação para os registros.
5. Se não for possível confirmar modelo, esforço ou independência do contexto,
   registre a limitação. O resultado esperado da tentativa é
   `UNABLE TO VERIFY`, sem substituição silenciosa por outro modelo.

Não há um comando de lançamento do Codex validado neste projeto. Use a interface
confirmada no seu ambiente, seguindo
[compatibility.md](skills/astramax-reviewer/references/compatibility.md).

### 3.2. Preparar uma entrega pequena e verificável

No projeto descartável da etapa 2, use Claude Code como autor no fluxo de
referência. Um exemplo de pedido:

> Crie um pequeno projeto Python, usando somente a biblioteca padrão, com uma
> função `pode_acessar(tenant_usuario, tenant_recurso)`. Ela deve retornar `True`
> somente quando os dois identificadores estiverem presentes e forem iguais.
> Identificadores ausentes, vazios ou diferentes devem resultar em `False`.
> Registre o contrato em uma especificação e documente um comando de testes
> com `unittest`. Implemente e teste os casos relevantes. Mantenha as mudanças
> disponíveis para uma revisão da árvore de trabalho.

Esse exemplo cria uma verificação pequena, com critérios objetivos e sem
dependência de Make, dbt, banco de dados ou serviços. Inspecione o comando de
teste documentado antes de executá-lo.

Depois, peça ao autor:

> Use astramax-reviewer para preparar a passagem desta entrega para uma revisão
> independente. Registre requisitos, escopo, comandos realmente executados,
> saídas, verificações ausentes, premissas de ambiente e decisões incertas.
> A preparação não deve ser apresentada como uma revisão do Astra.

O dossiê pode ser entregue na conversa ou em um arquivo solicitado. Se usar o
coletor, invoque o script pelo caminho real da instalação, passando o projeto
descartável em `--repo`. Não edite a skill para inserir comandos do projeto.
Consulte [handoff.md](skills/astramax-reviewer/references/handoff.md) para as
opções e os códigos de saída.

### 3.3. Executar a revisão

No contexto independente do Astra, abra o mesmo projeto e forneça o escopo,
a especificação e as evidências preparadas. Exemplo de pedido:

> Use astramax-reviewer para revisar a árvore de trabalho deste projeto contra
> a especificação da função de acesso. Inspecione o código e os testes de forma
> independente, estabeleça os comandos de verificação a partir do projeto e
> execute os checks pertinentes dentro das permissões existentes. Apresente
> achados com evidências, lacunas de verificação e um veredito. Não altere a
> implementação.

Confira o resultado:

- O revisor leu a especificação, a implementação e os testes, em vez de apenas
  concordar com as notas do autor.
- Os comandos vieram do projeto de teste; não apareceram alvos herdados como
  `make test` ou `make dbt-build` sem justificativa naquele projeto.
- O relatório identifica o contexto, a configuração real, o escopo e o estado
  sobre o qual os testes foram executados.
- Os resultados têm comandos, códigos de saída e saídas/logs verificáveis.
- Falhas, testes ausentes e hipóteses aparecem como tais, sem execução inventada.
- Os achados usam evidências reais e as gravidades previstas.
- Há um veredito coerente com as regras de
  [finding-severity.md](skills/astramax-reviewer/references/finding-severity.md).
- Não houve edição de implementação, commit, push ou exclusão automática de
  relatório. Use os diffs e o estado dos arquivos para conferir isso.

Uma revisão pode terminar corretamente sem achados. Não exija que o revisor
invente um defeito para provar que trabalhou.

### 3.4. Exercitar os casos de controle

Use execuções separadas e preserve o resultado de cada uma:

| Cenário | Procedimento | Resultado esperado |
| --- | --- | --- |
| Defeito conhecido | Apenas no projeto descartável, altere a função para permitir acesso quando `tenant_usuario` estiver ausente; mantenha a especificação original e revise a nova versão | Identificação do desvio com evidência de código ou reprodução, impacto e ação recomendada |
| Verificação indisponível | Solicite uma revisão sem permitir a execução do teste necessário e deixe a restrição explícita | Relatório declara que o teste não foi executado e aplica as regras de veredito à evidência disponível |
| Modelo/configuração não confirmados | Exercite o fluxo sem confirmação de Astra ou do esforço máximo | `UNABLE TO VERIFY`, sem alegar que o modelo desejado foi utilizado |
| Dossiê já existente | Gere outro dossiê para o mesmo caminho com o coletor | Recusa de sobrescrita e preservação do arquivo anterior |
| Pedido de implementação com dossiê pendente | Peça ao autor uma mudança explícita mantendo um relatório pendente | O autor segue o pedido atual; o arquivo sozinho não o obriga a assumir a revisão |

Para avaliar detecção independente no cenário de defeito conhecido, mantenha a
localização do defeito no registro do teste e forneça ao revisor os requisitos
e o escopo normal. Compare depois o relatório com o defeito introduzido.

**Concluído quando:** houver uma revisão real reproduzível, identificação do
defeito controlado e respeito aos limites de atuação. O teste de indisponibilidade
pode passar como teste de comportamento, mas não substitui a revisão real com
Astra disponível e confirmado.

## 4. Registrar versões, comandos e resultados

**Objetivo:** transformar os testes em um registro de compatibilidade confiável.

1. Atualize
   [references/compatibility.md](skills/astramax-reviewer/references/compatibility.md)
   com data, versões de Codex/Claude Code, modelo autor, modelo revisor, esforço
   efetivo e versões dos instaladores/validador realmente utilizados.
2. Atualize [docs/VALIDATION.md](docs/VALIDATION.md) com os procedimentos
   executados, saídas ou logs acessíveis, resultados e limitações.
3. Corrija os comandos de instalação no [README.md](README.md) e em
   [docs/PUBLISHING.md](docs/PUBLISHING.md) quando houver evidência de que a
   sintaxe original precisava mudar.
4. Preserve o histórico da validação local. Substitua o status “não verificado”
   somente para os itens efetivamente verificados.
5. Registre problemas encontrados como pendências concretas. Não transforme um
   teste parcial em uma declaração de suporte completo.

Modelo de registro para cada execução:

```text
Data e ambiente:
Commit completo / estado da árvore:
Etapa e cenário:
Ferramenta e versão:
Modelo e esforço, quando aplicável:
Fonte de confirmação da configuração:
Diretório de execução / instalação:
Comando ou prompt exato:
Código de saída, quando aplicável:
Saída ou caminho do log / relatório:
Resultado observado:
Critério de sucesso atendido: sim / não / parcial
Limitações e próxima ação:
```

**Concluído quando:** outra pessoa conseguir entender o que foi testado e repetir
o procedimento sem depender da memória de quem o executou.

## 5. Confirmar identidade e disponibilidade do pacote npm

**Objetivo:** escolher um nome publicável sob uma conta controlada pelo mantenedor.

Na raiz da origem, depois de preparar o acesso npm pelos meios normais da conta:

```bash
cd "$ASTRAMAX_FONTE"
npm whoami
npm view astramax-reviewer name version maintainers
```

1. Confirme que a conta retornada é a conta de publicação pretendida.
2. Verifique se o nome proposto já existe e, se existir, se a conta tem os
   direitos necessários. A resposta da consulta sozinha não concede esses direitos.
3. Não interprete erro de rede, autenticação ou uma resposta isolada como garantia
   de que o nome pode ser registrado.
4. Se necessário, escolha um escopo que a conta controle, como
   `@seu-usuario/astramax-reviewer`.
5. Ao mudar o nome npm, atualize `package.json`, README e exemplos de publicação.
   Preserve `astramax-reviewer` no frontmatter e no diretório da skill.
6. Confirme a versão a publicar e sua correspondência no changelog. Os exemplos
   seguintes usam `0.1.0`; ajuste-os se a versão efetiva mudar.

**Concluído quando:** nome, conta, permissões e versão pretendidos estiverem
confirmados. Esta etapa ainda não publica o pacote.

## 6. Testar o pacote real com SkillPM antes da publicação

**Objetivo:** comprovar que o arquivo que será distribuído funciona com o
gerenciador pretendido.

Na raiz da origem:

```bash
npm run validate
npm pack --dry-run --offline --cache .npm-cache
npm pack --offline --cache .npm-cache
```

1. Anote o nome efetivamente informado por `npm pack`. Para o nome e a versão
   atuais, o esperado é `astramax-reviewer-0.1.0.tgz`.
2. Inspecione o arquivo e registre seu hash. Ajuste o caminho abaixo se o nome
   ou a versão do pacote tiver mudado:

   ```bash
   ASTRAMAX_PACOTE="$ASTRAMAX_FONTE/astramax-reviewer-0.1.0.tgz"
   tar -tzf "$ASTRAMAX_PACOTE"
   sha256sum "$ASTRAMAX_PACOTE"
   ```

3. Confira o conjunto completo: `package.json`, README, LICENSE, CHANGELOG,
   SKILL, quatro referências e o coletor Python. Na estrutura atual são dez
   arquivos. Compare o conteúdo com a origem e confira os links relativos.
4. Confirme a ausência de credenciais, relatórios, caches, testes, material de
   portfólio e documentação de manutenção. `PROXIMOS_PASSOS.md` deve ficar
   fora do pacote, conforme a lista positiva de arquivos do manifesto.
5. Crie outro projeto descartável, separado do usado para a instalação GitHub:

   ```bash
   ASTRAMAX_TESTE_PACOTE="$(mktemp -d)"
   git -C "$ASTRAMAX_TESTE_PACOTE" init
   cd "$ASTRAMAX_TESTE_PACOTE"
   ```

6. Confirme a versão do SkillPM e sua forma documentada de instalar um arquivo
   `.tgz` local. Instale `ASTRAMAX_PACOTE` usando essa forma. Este repositório
   ainda não possui uma sintaxe de instalação local confirmada; não invente
   um argumento nem substitua esse teste por uma extração manual.
7. Se a versão escolhida não aceitar arquivos locais, documente a limitação e
   estabeleça uma alternativa real de teste anterior à publicação. Mantenha
   esta etapa pendente enquanto essa alternativa não for executada.
8. Na instalação testada, confirme a listagem usando a sintaxe verificada. O
   comando candidato registrado é:

   ```bash
   npx skillpm list
   ```

9. Confira nome, descrição, os seis arquivos da skill, referências e descoberta
   no host. Execute um teste curto de preparação e revisão com a instalação
   proveniente do pacote.
10. Registre os resultados da mesma maneira que nas etapas anteriores.

Se corrigir qualquer arquivo distribuído, gere outro pacote e repita os testes
afetados sobre ele. Mantenha o hash correspondente ao arquivo finalmente aprovado.

**Concluído quando:** o pacote real tiver sido instalado e reconhecido pelo
SkillPM e pelo host. O teste de extração que já passou na implementação local
não substitui esta etapa.

## 7. Fechar e identificar a versão de lançamento

**Objetivo:** garantir que documentação, commit, tag e pacote descrevam a mesma
versão aprovada.

1. Atualize README, changelog, compatibilidade e registros de validação com os
   resultados reais. Mantenha explicitamente pendente o teste via registro npm,
   que só poderá ocorrer após a publicação.
2. Ajuste o status de lançamento sem antecipar uma publicação ainda não feita.
   No momento da publicação, registre a data e a versão efetivas.
3. Se essas atualizações mudarem arquivos empacotados, volte à etapa 6 para
   gerar, conferir e testar o pacote atualizado.
4. Na origem, revise as alterações. Adicione somente os arquivos pertencentes
   ao lançamento. Um exemplo, quando esses forem os arquivos alterados:

   ```bash
   cd "$ASTRAMAX_FONTE"
   git status --short
   git diff --check
   git add README.md CHANGELOG.md package.json skills/astramax-reviewer docs PROXIMOS_PASSOS.md
   git diff --cached --stat
   git diff --cached --check
   git diff --cached
   git commit -m "Prepare validated AstraMax Reviewer 0.1.0 release"
   ```

5. Confira que não há mudanças distribuídas fora do commit e que o pacote
   aprovado ainda corresponde a essa origem. Não é necessário recriar um
   pacote apenas porque foi feito um commit; seus arquivos precisam coincidir.
6. Quando o lançamento estiver aprovado, crie e envie a tag e a branch. Antes,
   confira se a tag já existe; não a sobrescreva. Para a versão atual:

   ```bash
   git tag --list v0.1.0
   git tag -a v0.1.0 -m "AstraMax Reviewer 0.1.0"
   git push origin main
   git push origin v0.1.0
   ```

   Execute a criação somente se a consulta não mostrar uma tag existente. Se
   ela já existir, confira a qual commit pertence e resolva a versão do lançamento
   antes de continuar. Execute o push da branch a partir da `main` pretendida.

7. Confirme que o remoto contém o commit e a tag corretos. Se a skill distribuída
   mudou desde a instalação GitHub testada, repita esse teste com a versão final.

**Concluído quando:** a versão final estiver identificada no Git e o pacote
aprovado corresponder aos arquivos daquele commit.

## 8. Publicar no npm o arquivo aprovado

**Objetivo:** publicar exatamente o pacote já inspecionado e testado.

Esta é a etapa de publicação. Execute-a somente no lançamento solicitado, após
as etapas anteriores terem sido concluídas.

1. Confirme novamente conta, nome, versão e hash do arquivo aprovado.
2. Confira que os registros não têm falhas de aceitação pendentes.
3. Publique o arquivo da etapa 6, usando seu caminho real:

   ```bash
   npm whoami
   sha256sum "$ASTRAMAX_PACOTE"
   npm publish "$ASTRAMAX_PACOTE" --access public
   ```

4. Registre a saída, o código de saída e a identificação exata da versão
   publicada. Não trate uma tentativa sem confirmação como publicação concluída.
5. Se houver falha, preserve o erro e resolva sua causa. Não gere nem publique
   outro conteúdo sob uma versão diferente apenas para contornar a falha sem
   avaliar o que aconteceu.

**Concluído quando:** o registro npm confirmar a publicação do nome e da versão
esperados, provenientes do arquivo aprovado.

## 9. Validar a instalação publicada e concluir a divulgação

**Objetivo:** comprovar o caminho que um usuário novo seguirá.

1. Use outro projeto limpo, que ainda não tenha recebido a skill por GitHub ou
   arquivo local. Isso evita confundir a instalação anterior com a nova.
2. Com a sintaxe e o nome confirmados, execute os comandos de instalação e
   listagem. Para o nome não escopado previsto originalmente:

   ```bash
   npx skillpm install astramax-reviewer
   npx skillpm list
   ```

3. Confira a versão realmente obtida; não presuma que ela é a pretendida apenas
   porque a instalação terminou. Se necessário, use a seleção de versão
   documentada pelo instalador e registre o comando utilizado.
4. Confira nome, descrição, referências, arquivos e reconhecimento pelo host.
   Faça uma revisão curta para confirmar o funcionamento da instalação publicada.
5. Atualize a documentação com o resultado pós-publicação e remova apenas os
   avisos de pendência que agora têm comprovação. Registre a publicação efetiva
   no changelog. Novas alterações no repositório não modificam o pacote já publicado.
6. No GitHub, confira descrição, licença, README e tópicos relacionados ao projeto.
   Consulte [docs/PUBLISHING.md](docs/PUBLISHING.md) para a lista proposta.
7. Verifique a descoberta no SkillsMP pelo caminho documentado pelo próprio
   serviço. Registre o resultado separadamente: publicar no GitHub não comprova
   que um índice já encontrou a skill. Preserve uma única fonte canônica.
8. Anuncie o suporte a npm/SkillPM somente depois do teste da instalação publicada.
   Informe a versão testada e as limitações que permanecerem.

Se o teste pós-publicação falhar, registre a falha e corrija o problema antes
de anunciar que o fluxo funciona. Preserve a rastreabilidade da versão afetada.

**Concluído quando:** um ambiente limpo conseguir instalar e usar a versão
publicada, a documentação refletir os resultados reais e o estado de descoberta
nos índices estiver registrado sem promessas não verificadas.

## Checklist de acompanhamento

- [ ] 0. Commit, estado local e ambiente de teste registrados.
- [ ] 1. Validador oficial aprovado.
- [ ] 2. Instalação GitHub e descoberta no host aprovadas.
- [ ] 3. Revisão real e cenários controlados aprovados.
- [ ] 4. Versões, comandos, saídas e limitações documentados.
- [ ] 5. Conta, nome npm e versão de lançamento confirmados.
- [ ] 6. Pacote real instalado e testado com SkillPM antes da publicação.
- [ ] 7. Commit/tag finais e pacote aprovado correspondentes.
- [ ] 8. Publicação npm confirmada.
- [ ] 9. Instalação publicada validada e documentação/divulgação atualizadas.

Não marque uma etapa por inferência a partir de outra. Formato válido, instalação
correta, revisão útil e publicação bem-sucedida são verificações diferentes.
