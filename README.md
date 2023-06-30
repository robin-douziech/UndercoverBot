# UndercoverBot

UndercoverBot est une bot discord permettant de jouer au jeu undercover.

## Règles du jeu

Dans undercover, il y a trois camps : les civils, les undercovers et Mr. White.

Au début de la partie, tous les civils reçoivent un mot secret (ils ont tous le même).
Les undercovers reçoivent aussi un mot secret, différent de celui des civils, mais assez proche de celui-ci.
Mr. White, lui, ne reçoit aucun mot.

Le but des civils est de démasquer Mr. White et les undercovers et de les éliminer.
Le but des undercovers est d'éliminer assez de civils pour qu'il reste au moins autant d'undercovers que de civils (et d'éliminer Mr. White).
Le but de Mr. White est de rester le plus longtemps possible dans la partie. Quand il se fera éliminer, il aura une occasion de tenter de deviner le mot des civils pour remporter la partie.

Déroulement de la partie :

Chacun leur tour à partir d'un joueur désigné au hasard, les joueurs disent un mot en rapport avec le mot qu'ils ont reçu en début de partie (ou en rapport avec les mots qui ont été dit par les autres joueurs s'ils n'ont pas reçu de mot). Une fois que chaque joueur a dit un mot, on vote pour éliminer un joueur. Le rôle du joueur éliminé est annoncé. Si c'est Mr. White, il tente de deviner le mot de civils.

## Jouer avec le bot

### S'inscrire à une partie

`!play <arg>` 

pour s'inscrire     : arg = { True | true | T | t | Yes | yes | Y | y | 1 }
pour se désinscrire : arg = { False | false | F | f | No | no | N | n | 0 }

### Voter pour un joueur

`!vote <player>`

Vous pouvez voter à n'importe quel moment, tous les votes seront pris en compte en même temps.

### Tenter de deviner le mot des civils (Mr. White)

`!guess <word>`

Vous pouvez tenter de deviner le mot à n'importe quel moment, le mot que vous avez renseigné sera pris en compte quand vous serez désigné par le vote. Tant que vous êtes en vie, vous pouvez modifier le mot que vous voulez mette avec la même commande. Vous pouvez supprimer ce mot avec `!guess Null`. Si vous n'avez pas encore renseigné de mot quand vous êtes désigné par le vote, le bot attendra que vous en ayez renseigné un avant de continuer la partie.