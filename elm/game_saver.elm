module GameSaver where
{-| Elm app for saving foosball games
-}
import Char
import Html exposing (..)
import Html.Attributes as Attr exposing (..)
import Html.Events exposing (..)
import Html.Lazy exposing (lazy, lazy2, lazy3)
import Http
import Json.Decode as Json exposing ((:=))
import Json.Encode
import String
import Task exposing (..)
import Signal exposing (Signal, Address)

---- MODEL ----
type alias Model =
    { players : List Player
    , field : String
    , uid : Int
    , visibility : String
    }


type alias Player =
    { name : String
    , editing : Bool
    , id : Int
    , winner : Bool
    }


newPlayer : String -> Int -> Bool -> Player
newPlayer pname id isWin =
    { name = pname
    , editing = False
    , id = id
    , winner = isWin
    }

emptyModel : Model
emptyModel =
    { players = []
    , visibility = "All"
    , field = ""
    , uid = 1
    }

-- UPDATE
type Action = NoOp |
              Add |
              UpdateField String |
              Delete Int |
              DeleteComplete |
              EditingPlayer Int Bool |
              UpdatePlayer Int String

-- How we update our Model on a given Action?
update : Action -> Model -> Model
update action model =
    let mod = if action == Add then 1 else -1
        winMark = ((List.length model.players) + mod)//2
        assignWinners = (\i p -> {p | winner <- i < winMark})
    in
    case action of
      NoOp -> model

      Add ->
          let playersPlusAdd = if String.isEmpty model.field
                                 then model.players
                                 else model.players ++ [newPlayer model.field model.uid False]
              nuPlayers = List.indexedMap assignWinners playersPlusAdd
          in
          { model |
              uid <- model.uid + 1,
              field <- "",
              players <- nuPlayers
          }

      UpdateField str ->
          { model | field <- str }

      EditingPlayer id isEditing ->
          let updatePlayer t = if t.id == id then { t | editing <- isEditing }
                                             else t
          in
              { model | players <- List.map updatePlayer model.players }

      UpdatePlayer id player ->
          let updatePlayer t = if t.id == id then { t | name <- player } else t
          in
              { model | players <- List.map updatePlayer model.players }

      Delete id ->
          { model | players <- List.indexedMap assignWinners
                                (List.filter (\t -> t.id /= id) model.players) }

-- VIEW
view : Address Action -> Model -> Html
view address model =
    div
      [ class "fbrec-wrapper" ]
      [ section
          [ id "fb_record" ]
          [ lazy3 playerEntry address model.field ((List.length model.players)+1)
          , lazy2 playerList address model.players
          ]
      ]


playerEntry : Address Action -> String -> Int -> Html
playerEntry address player nextPnum =
    let isDisabled = nextPnum >= 5
        pholder = if isDisabled then "Max Players" else
                   "Enter player " ++ toString nextPnum ++ " name"
        gameName = case nextPnum - 1 of
                     2 -> "1v1"
                     3 -> "King of the Hill"
                     4 -> "2v2"
                     _ -> "Enter a player name"
    in
    header
        [ id "header" ]
        [ h1 [] [ text gameName ]
        , input
            [ id "new-player"
            , placeholder pholder
            , autofocus True
            , value player
            , disabled isDisabled
            , name "newPlayer"
            , on "input" targetValue (Signal.message address << UpdateField)
            , onEnter address Add
            ]
            []
        ]

playerList : Address Action -> List Player -> Html
playerList addr players =
    section
      [ id "main" ]
      [ ul [ id "player-list", class "list-group" ]
           (List.indexedMap (playerItem addr) players) ]

playerItem : Address Action -> Int -> Player -> Html
playerItem addr pnum playa =
    li
      [ classList [("editing", playa.editing),
                   ("list-group-item-success", playa.winner),
                   ("list-group-item-danger", not playa.winner),
                   ("list-group-item", True)]]
      [ div
          [ class "playerItem" ]
          [ label
              [ onDoubleClick addr (EditingPlayer playa.id True) ]
              [ text ("Player " ++ toString (pnum+1) ++ ": " ++ playa.name) ]
          , button [ class "btn btn-danger closebutton",
                     onClick addr (Delete playa.id) ]
          [ span [class "glyphicon glyphicon-remove",
                 property "aria-hidden" (Json.Encode.string "true")]
           []
          ]
          ]
      ]

onEnter : Address a -> a -> Attribute
onEnter address value =
    on "keydown"
      (Json.customDecoder keyCode is13)
      (\_ -> Signal.message address value)


is13 : Int -> Result String ()
is13 code =
  if code == 13 then Ok () else Err "not the right key code"

-- WIRING
---- INPUTS ----

-- wire the entire application together
main : Signal Html
main =
  Signal.map (view actions.address) model


-- manage the model of our application over time
model : Signal Model
model =
  Signal.foldp update initialModel actions.signal


initialModel : Model
initialModel =
  Maybe.withDefault emptyModel getStorage


-- actions from user input
actions : Signal.Mailbox Action
actions =
  Signal.mailbox NoOp

-- interactions with server to save the model
port getStorage : Maybe Model

port setStorage : Signal Model
port setStorage = model