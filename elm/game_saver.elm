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
import Json.Encode as Encode
import String
import Task exposing (..)
import Signal exposing (Signal, Address, (<~))

---- MODEL ----
type alias Model =
    { players : List Player
    , field : String
    , saveThis : Bool
    }


type alias Player =
    { name : String
    , editing : Bool
    , pnum : Int
    , winner : Bool
    }

encodePlayer : Player -> Encode.Value
encodePlayer p = Encode.object [ ("name", Encode.string p.name) ]


newPlayer : String -> Int -> Bool -> Player
newPlayer pname pnum isWin =
    { name = pname
    , editing = False
    , pnum = pnum
    , winner = isWin
    }

emptyModel : Model
emptyModel =
    { players = []
    , saveThis = False
    , field = ""
    }

-- UPDATE
type Action = NoOp |
              Add |
              UpdateField String |
              Delete Int |
              DeleteComplete |
              EditingPlayer Int Bool |
              UpdatePlayer Int String |
              SaveGame |
              Clear Bool

-- How we update our Model on a given Action?
update : Action -> Model -> Model
update action model =
    let mod = if action == Add then 1 else -1
        plength = List.length model.players
        winMark = (plength + mod)//2
        assignWinners = (\i p -> {p | winner <- i < winMark})
    in
    case action of
      NoOp -> model

      Add ->
          let playersPlusAdd = if String.isEmpty model.field
                                 then model.players
                                 else model.players ++ [newPlayer model.field (plength+1) False]
              nuPlayers = List.indexedMap assignWinners playersPlusAdd
          in
          { model |
              field <- "",
              players <- nuPlayers
          }

      UpdateField str ->
          { model | field <- str }

      EditingPlayer pnum isEditing ->
          let updatePlayer t = if t.pnum == pnum then { t | editing <- isEditing }
                                             else t
          in
              { model | players <- List.map updatePlayer model.players }

      UpdatePlayer pnum player ->
          let updatePlayer t = if t.pnum == pnum then { t | name <- player } else t
          in
              { model | players <- List.map updatePlayer model.players }

      Delete pnum ->
          { model | players <- List.indexedMap assignWinners
                                (List.filter (\t -> t.pnum/=pnum) model.players) }

      SaveGame ->
          let encodedPlist =
                  Encode.encode 0
                    (Encode.object [ ("players",
                     Encode.list (List.map encodePlayer model.players) ) ])
          in
          { model | saveThis <- True }

      Clear b -> if b then emptyModel else { model | saveThis <- False }

-- VIEW
view : Address Action -> Model -> Html
view address model =
    let saveDisabled = (List.length model.players) <= 1
    in
    div
      [ class "fbrec-wrapper" ]
      [ section
          [ id "fb_record" ]
          [ lazy3 playerEntry address model.field ((List.length model.players)+1)
          , lazy2 playerList address model.players
          , footer [] [ button [ id "savegame",
                                 classList [("btn btn-success btn-lg", True),
                                            ("disabled", saveDisabled)],
                                 disabled saveDisabled,
                                 onClick address SaveGame
                               ]
                        [text "Save Game!"] ]
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
              [ onDoubleClick addr (EditingPlayer playa.pnum True) ]
              [ text ("Player " ++ toString (pnum+1) ++ ": " ++ playa.name) ]
          , button [ class "btn btn-danger closebutton",
                     onClick addr (Delete playa.pnum) ]
          [ span [class "glyphicon glyphicon-remove",
                 property "aria-hidden" (Encode.string "true")]
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
  (view actions.address) <~ modelSig


-- manage the model of our application over time
modelSig : Signal Model
modelSig =
  Signal.foldp update emptyModel (Signal.merge actions.signal (Clear <~ wipeModel))

-- actions from user input
actions : Signal.Mailbox Action
actions =
  Signal.mailbox NoOp

-- Mailbox for when we want to save
saver : Signal.Mailbox String
saver = Signal.mailbox ""

-- interactions with server to save the model
-- Only save when we have something to save.
port setStorage : Signal Model
port setStorage = Signal.filter (\m -> m.saveThis) emptyModel modelSig

-- We'll have JS send us a signal back when it's OK to wipe the model on save
port wipeModel : Signal Bool
