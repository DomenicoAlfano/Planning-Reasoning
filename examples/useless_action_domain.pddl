(define (domain useless-action)

  (:predicates
   (succ ?i1 ?i2)
   (at ?what ?x ?y)
   (robot ?who)
   (bag ?what)
   (picked ?r ?what)
  )
   
   (:action moveRight
    :parameters (?r ?x1 ?x2 ?y)
    :precondition (and
                    (robot ?r)
                    (succ ?x1 ?x2)
                    (at ?r ?x1 ?y)
                    )
    :effect (and
              (at ?r ?x2 ?y)
              (not (at ?r ?x1 ?y)))
  )

  (:action moveLeft
    :parameters (?r ?x2 ?x1 ?y)
    :precondition (and
                    (robot ?r)
                    (succ ?x1 ?x2)
                    (at ?r ?x2 ?y)
                    )
    :effect (and
              (at ?r ?x1 ?y)
              (not (at ?r ?x2 ?y)))
  )

  (:action moveUp
    :parameters (?r ?x ?y1 ?y2)
    :precondition (and
                    (robot ?r)
                    (succ ?y1 ?y2)
                    (at ?r ?x ?y1)
                    )
    :effect (and
              (at ?r ?x ?y2)
              (not (at ?r ?x ?y1)))
  )

  (:action moveDown
    :parameters (?r ?x ?y2 ?y1)
    :precondition (and
                    (robot ?r)
                    (succ ?y1 ?y2)
                    (at ?r ?x ?y2)
                    )
    :effect (and
              (at ?r ?x ?y1)
              (not (at ?r ?x ?y2)))
  )

  (:action pickObject
    :parameters (?r ?b ?x ?y)
    :precondition (and
                    (robot ?r)
                    (bag ?b)
                    (at ?r ?x ?y)
                    (at ?b ?x ?y)
                  )
    :effect (and
              (not (at ?b ?x ?y))
              (picked ?r ?b)
              )
  )

)
